#!/usr/bin/env python3
"""Ban inline scripts and file templates inside customization files.

Enforces the **Script it or template it — never inline it** rule from
.github/copilot-instructions.md for instruction and agent files.
Reusable executable logic must live in .github/scripts/ and be *called*;
repeated file skeletons must live in .github/templates/ and be *linked*.
Only short illustrative examples may appear inline.

Scope (skills are intentionally excluded — they are reference docs):
  - .github/instructions/**
  - .github/agents/**

Checks performed (per fenced code block):
  - inline-script   : a fenced block in an executable language that is a
                      *reusable script* (contains loop / function constructs,
                      or is long) rather than a one-off command example.
  - inline-template : a fenced block that reproduces a file skeleton
                      (YAML frontmatter followed by a markdown heading, or a
                      ```markdown block with multiple headings).

Allowed without complaint:
  - Blocks that *call* an extracted artifact (reference `.github/scripts/`
    or `.github/templates/`).
  - Short command examples (no control flow, under the line threshold).
  - Any block explicitly marked as an example: place `<!-- example -->`
    on the line immediately before the opening fence.

Usage:
  python check-customization-inline-logic.py [REPO_ROOT]            # full scan
  echo "file1\\nfile2" | python check-customization-inline-logic.py --stdin

Exit code 0 = all clean, 1 = violations found.
"""

import os
import re
import subprocess
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCOPE_DIRS = (
    os.path.join(".github", "instructions"),
    os.path.join(".github", "agents"),
)

EXEC_LANGS = {
    "powershell", "pwsh", "ps1", "ps",
    "bash", "sh", "shell", "zsh", "ksh",
    "python", "py",
    "cmd", "bat", "batch",
}

TEMPLATE_LANGS = {"markdown", "md"}

# Reusable-logic signals: loops and function definitions. A bare `if` is
# deliberately excluded — a single conditional is still an example, not a
# script. Pipeline operators like ForEach-Object / % are not loops here.
CONTROL_FLOW = re.compile(
    r"(?im)^\s*(?:"
    r"for\s*\(|for\s+\$?\w+\s+in\b|"
    r"foreach\s*\(|foreach\s+\$?\w+\b|"
    r"while\s*\(|while\s+\[|while\s+\w|"
    r"do\s*\{|"
    r"function\s+[\w-]+|"
    r"def\s+\w+\s*\("
    r")"
)

ARTIFACT_REF = re.compile(r"\.github[\\/](?:scripts|templates)[\\/]", re.IGNORECASE)
EXAMPLE_MARKER = re.compile(r"<!--\s*example\b.*?-->", re.IGNORECASE)
HEADING = re.compile(r"^#{1,6}\s+\S")
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([^\s`~]*)")

# A block of executable code with this many or more non-blank lines is treated
# as a script even without explicit control flow.
LINE_THRESHOLD = 12

# Structured-config languages whose fenced blocks may be a full file skeleton
# (e.g. a hook JSON pasted into an instruction) and must be extracted to a script or
# template. Detection is prose-gated to avoid flagging the many short
# illustrative frontmatter / config snippets that legitimately appear inline.
CONFIG_LANGS = {"json", "jsonc", "json5", "yaml", "yml", "xml", "toml"}

# Prose immediately above a fence that instructs the AI to materialise the block
# as a file on disk. Matched against the few nearest non-blank lines above.
FILE_CREATION = re.compile(
    r"(?i)(?:"
    r"creat\w*\s+(?:the\s+|a\s+|this\s+)?(?:temporary\s+)?(?:hook\s+)?file\b|"
    r"with\s+(?:exactly\s+)?this\s+content\b|"
    r"with\s+the\s+following\s+content\b|"
    r"containing\s+(?:exactly\s+)?this\b|"
    r"writ\w*\s+(?:the\s+|a\s+|this\s+)?file\b|"
    r"sav\w*\s+(?:the\s+|a\s+|this\s+)?(?:as\s+a\s+)?file\b"
    r")"
)

# A config block must reach this many non-blank lines before it counts as a
# full document skeleton rather than a one- or two-line illustrative snippet.
CONFIG_DOC_MIN_LINES = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _in_scope(rel_path: str) -> bool:
    rel = rel_path.replace("/", os.sep)
    return any(rel == d or rel.startswith(d + os.sep) for d in SCOPE_DIRS)


def find_scope_files(repo_root: str):
    """Yield relative paths to tracked .md files within the scoped dirs."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "*.md"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        paths = [p for p in result.stdout.split("\0") if p]
    except (FileNotFoundError, subprocess.CalledProcessError):
        paths = None

    if paths is not None:
        for rel in paths:
            rel_os = rel.replace("/", os.sep)
            if _in_scope(rel_os):
                yield rel_os
    else:
        for dirpath, dirnames, filenames in os.walk(repo_root):
            for fname in filenames:
                if fname.lower().endswith(".md"):
                    rel = os.path.relpath(os.path.join(dirpath, fname), repo_root)
                    if _in_scope(rel):
                        yield rel


def _prev_nonblank(lines, idx):
    """Return the nearest non-blank line above index *idx*, or ''."""
    j = idx - 1
    while j >= 0:
        if lines[j].strip():
            return lines[j].strip()
        j -= 1
    return ""


def _preceded_by_file_creation(lines, open_line, lookback=4):
    """True if a file-creation instruction sits just above the fence.

    Scans the *lookback* nearest non-blank lines above *open_line* for prose
    that tells the AI to write the following block out as a file.
    """
    seen = 0
    j = open_line - 1
    while j >= 0 and seen < lookback:
        line = lines[j].strip()
        if line:
            if FILE_CREATION.search(line):
                return True
            seen += 1
        j -= 1
    return False


def _looks_like_config_document(lang, body):
    """True if the block is a complete structured-config document."""
    nonblank = [ln.strip() for ln in body if ln.strip()]
    if len(nonblank) < CONFIG_DOC_MIN_LINES:
        return False
    first = nonblank[0]
    if lang in ("json", "jsonc", "json5"):
        return first.startswith("{") or first.startswith("[")
    if lang == "xml":
        return first.startswith("<")
    if lang in ("yaml", "yml"):
        keyish = sum(1 for ln in nonblank if re.match(r"^[\w.-]+\s*:", ln))
        return keyish >= 2
    if lang == "toml":
        return any(re.match(r"^\[.+\]\s*$", ln) for ln in nonblank) or \
            sum(1 for ln in nonblank if re.match(r"^[\w.-]+\s*=", ln)) >= 2
    return False


def _looks_like_template(lang, body):
    """True if the block body reproduces a file skeleton."""
    nonblank = [ln for ln in body if ln.strip()]

    # ```markdown / ```md block with two or more headings = a document skeleton.
    if lang in TEMPLATE_LANGS and sum(1 for ln in body if HEADING.match(ln)) >= 2:
        return True

    # YAML frontmatter (--- ... ---) followed by a markdown heading = a .md file.
    stripped = [ln.rstrip() for ln in body]
    if nonblank and nonblank[0].strip() == "---":
        try:
            first = next(i for i, ln in enumerate(stripped) if ln.strip() == "---")
            second = next(
                i for i, ln in enumerate(stripped)
                if i > first and ln.strip() == "---"
            )
        except StopIteration:
            second = None
        if second is not None:
            tail = body[second + 1:]
            if any(HEADING.match(ln) for ln in tail):
                return True
    return False


def validate_file(rel_path, repo_root):
    """Return a list of (line_no, type, detail) violations for one file."""
    full = os.path.join(repo_root, rel_path)
    try:
        with open(full, "r", encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except (OSError, UnicodeDecodeError):
        return []

    violations = []
    i = 0
    n = len(lines)
    while i < n:
        m = FENCE.match(lines[i])
        if not m:
            i += 1
            continue

        fence_token = m.group(2)
        lang = m.group(3).strip().lower()
        open_line = i
        marker_line = _prev_nonblank(lines, open_line)
        is_example = bool(EXAMPLE_MARKER.search(marker_line))

        # Collect body until the matching closing fence.
        body = []
        j = i + 1
        closed = False
        while j < n:
            cm = FENCE.match(lines[j])
            if cm and cm.group(2)[0] == fence_token[0] \
                    and len(cm.group(2)) >= len(fence_token) \
                    and cm.group(3).strip() == "":
                closed = True
                break
            body.append(lines[j])
            j += 1

        block_text = "\n".join(body)
        references_artifact = bool(ARTIFACT_REF.search(block_text))
        nonblank_count = sum(1 for ln in body if ln.strip())

        if not is_example and not references_artifact:
            if lang in EXEC_LANGS:
                if CONTROL_FLOW.search(block_text) or nonblank_count >= LINE_THRESHOLD:
                    reason = (
                        "control-flow logic"
                        if CONTROL_FLOW.search(block_text)
                        else f"{nonblank_count} lines"
                    )
                    violations.append((
                        open_line + 1,
                        "inline-script",
                        f"Inline {lang} script ({reason}) — extract to "
                        f".github/scripts/ and call it, or mark the block "
                        f"<!-- example --> if it is only illustrative",
                    ))
            elif _looks_like_template(lang, body):
                violations.append((
                    open_line + 1,
                    "inline-template",
                    "Inline file skeleton — extract to .github/templates/ and "
                    "link it, or mark the block <!-- example --> if it is only "
                    "illustrative",
                ))

        # Config-file skeletons (json/yaml/xml/toml the prose says to *create*)
        # are flagged even when they name a .github/scripts path — a skeleton
        # that merely references a script is still a skeleton, not a call.
        if not is_example and lang in CONFIG_LANGS \
                and _looks_like_config_document(lang, body) \
                and _preceded_by_file_creation(lines, open_line):
            violations.append((
                open_line + 1,
                "inline-template",
                f"Inline {lang} file skeleton — the prose tells the AI to "
                f"create this file; extract the file's content into a "
                f".github/scripts/ install script (or a .github/templates/ "
                f"template) and call/link it, or mark the block "
                f"<!-- example --> if it is only illustrative",
            ))

        i = j + 1 if closed else j

    return violations


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")

    use_stdin = "--stdin" in sys.argv
    repo_root = os.path.abspath(".")
    for arg in sys.argv[1:]:
        if arg != "--stdin":
            repo_root = os.path.abspath(arg)
            break

    if use_stdin:
        files = [f.strip() for f in sys.stdin.read().splitlines() if f.strip()]
        files = [
            f.replace("/", os.sep) for f in files
            if f.lower().endswith(".md") and _in_scope(f)
        ]
    else:
        files = list(find_scope_files(repo_root))

    all_violations = []
    files_checked = 0
    for rel_path in files:
        if not os.path.isfile(os.path.join(repo_root, rel_path)):
            continue
        files_checked += 1
        for line_no, vtype, detail in validate_file(rel_path, repo_root):
            all_violations.append((rel_path, line_no, vtype, detail))

    is_ci = os.environ.get("CI") == "true"

    if is_ci:
        for rel_path, line_no, vtype, detail in all_violations:
            gh_path = rel_path.replace(os.sep, "/")
            print(f"::error file={gh_path},line={line_no}::[{vtype}] {detail}")

    print()
    print(f"Scanned {files_checked} customization file(s).")

    if all_violations:
        by_type = defaultdict(int)
        for _, _, t, _ in all_violations:
            by_type[t] += 1

        print(f"Found {len(all_violations)} inline-logic violation(s):")
        for t, c in sorted(by_type.items()):
            print(f"  {t}: {c}")

        by_file = defaultdict(list)
        for rel_path, line_no, vtype, detail in all_violations:
            by_file[rel_path.replace(os.sep, "/")].append((line_no, vtype, detail))

        print()
        print("Files with violations:")
        for filepath in sorted(by_file):
            print(f"  {filepath}")
        print()
        for filepath, issues in sorted(by_file.items()):
            print(f"  {filepath}")
            for line_no, vtype, detail in sorted(issues):
                print(f"    Line {line_no}: [{vtype}] {detail}")
            print()

        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## 🚫 Inline Script / Template Violations\n\n")
                sf.write(
                    f"Scanned **{files_checked}** files, found "
                    f"**{len(all_violations)}** violation(s) in "
                    f"**{len(by_file)}** file(s).\n\n"
                )
                sf.write("### Files with violations\n\n")
                for filepath in sorted(by_file):
                    sf.write(f"- `{filepath}`\n")
                sf.write("\n| Type | File | Line | Detail |\n")
                sf.write("|------|------|-----:|--------|\n")
                for rel_path, line_no, vtype, detail in all_violations:
                    gh_path = rel_path.replace(os.sep, "/")
                    safe = detail.replace("|", "\\|")
                    sf.write(f"| `{vtype}` | `{gh_path}` | {line_no} | {safe} |\n")

        sys.exit(1)

    print("No inline scripts or templates found. ✅")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as sf:
            sf.write("## 🚫 Inline Script / Template Check\n\n")
            sf.write(
                f"Scanned **{files_checked}** files — no inline scripts or "
                f"templates. ✅\n"
            )


if __name__ == "__main__":
    main()
