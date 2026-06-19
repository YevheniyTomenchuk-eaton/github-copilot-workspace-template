#!/usr/bin/env python3
"""Validate markdown links across the repository.

Checks every .md file (except excluded directories) for:
  - missing    : target file does not exist
  - folder     : link points to a directory instead of a file
  - escaped    : relative path resolves outside the repository root

Usage:
  python check-markdown-links.py [REPO_ROOT]

Exit code 0 = all links valid, 1 = broken links found.
"""

import os
import re
import subprocess
import sys
from urllib.parse import unquote as url_unquote

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Directories whose .md files are skipped entirely.
# .github/templates — links are relative to the copy-destination, not actual location.
# .github/prompts   — reference / instructional content, not published.
EXCLUDED_DIRS = (
    os.path.join(".github", "templates"),
    os.path.join(".github", "prompts"),
)

# Regex: markdown link  [text](target)  or image  ![alt](target)
# Captures the raw target string inside the parentheses.
LINK_RE = re.compile(r"!?\[(?:[^\[\]\\]|\\.)*\]\(([^)]+)\)")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _in_dir(rel_path: str, dirs: tuple[str, ...]) -> bool:
    """True if *rel_path* is inside any of *dirs*."""
    return any(rel_path == d or rel_path.startswith(d + os.sep) for d in dirs)


def find_md_files(repo_root: str):
    """Yield absolute paths to tracked .md files, honoring exclusions.

    Uses ``git ls-files`` so gitignored directories are excluded
    automatically — no hardcoded list needed. Falls back to a plain
    filesystem walk when git is unavailable.
    """
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
        # git not available — fall back to filesystem walk.
        paths = None

    if paths is not None:
        for rel in paths:
            rel_os = rel.replace("/", os.sep)
            if _in_dir(rel_os, EXCLUDED_DIRS):
                continue
            yield os.path.join(repo_root, rel_os)
    else:
        for dirpath, dirnames, filenames in os.walk(repo_root):
            rel = os.path.relpath(dirpath, repo_root)
            if _in_dir(rel, EXCLUDED_DIRS):
                dirnames.clear()
                continue
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") or d == ".github"
            ]
            for fname in filenames:
                if fname.lower().endswith(".md"):
                    yield os.path.join(dirpath, fname)


def extract_links(filepath: str):
    """Return list of (line_number, raw_target) from *filepath*.

    Fenced code blocks (``` / ~~~), HTML comments, inline code, and
    strikethrough spans are skipped.
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    results: list[tuple[int, str]] = []
    in_code_block = False
    in_html_comment = False

    for idx, raw_line in enumerate(lines):
        line = raw_line.rstrip("\r\n")
        stripped = line.strip()

        # --- fenced code block toggle ---
        if not in_html_comment and (
            stripped.startswith("```") or stripped.startswith("~~~")
        ):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # --- HTML comment handling (<!-- ... -->) ---
        if in_html_comment:
            if "-->" in line:
                in_html_comment = False
                line = line[line.index("-->") + 3 :]
            else:
                continue

        # Remove inline HTML comments that open and close on the same line.
        line = re.sub(r"<!--.*?-->", "", line)

        if "<!--" in line:
            line = line[: line.index("<!--")]
            in_html_comment = True

        # Remove inline code spans (links inside backticks are examples).
        line = re.sub(r"``[^`]*``", "", line)
        line = re.sub(r"`[^`]*`", "", line)

        # Remove strikethrough spans (~~...~~) — "don't do this" examples.
        line = re.sub(r"~~.*?~~", "", line)

        # --- extract markdown links ---
        for m in LINK_RE.finditer(line):
            target = m.group(1).strip()

            # Strip optional title:  path "title"  or  path 'title'
            for sep in (' "', " '"):
                if sep in target:
                    target = target[: target.index(sep)]
                    break

            # Skip external links, anchors, and placeholders.
            if target.lower().startswith(("http://", "https://", "mailto:", "ftp://", "tel:", "data:")):
                continue
            if target.startswith("#"):
                continue
            if re.fullmatch(r"\.{3,}|PLACEHOLDER.*", target):
                continue

            # --- Relative link ---
            path_part = target.split("#")[0].strip()
            if path_part:
                results.append((idx + 1, path_part))

    return results


def validate_relative_link(filepath: str, target: str, repo_root: str):
    """Return (error_type, detail) or None if valid."""
    file_dir = os.path.dirname(filepath)
    decoded_target = url_unquote(target)
    resolved = os.path.normpath(os.path.join(file_dir, decoded_target))

    # Path must stay inside the repo.
    if not resolved.startswith(repo_root):
        return (
            "escaped",
            f"Resolves outside repository root → {os.path.relpath(resolved, repo_root)}",
        )

    # Directory link — should point to a file (usually README.md).
    if os.path.isdir(resolved):
        return (
            "folder",
            f"Links to a directory — use an explicit file, e.g. {target}/README.md",
        )

    # File does not exist.
    if not os.path.isfile(resolved):
        rel_target = os.path.relpath(resolved, repo_root)
        return ("missing", f"Target does not exist → {rel_target}")

    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Ensure UTF-8 output (Windows terminals default to cp1252).
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")

    repo_root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    errors: list[tuple[str, int, str, str, str]] = []

    files_checked = 0
    links_checked = 0

    for filepath in find_md_files(repo_root):
        files_checked += 1
        rel_file = os.path.relpath(filepath, repo_root)

        links = extract_links(filepath)
        for line_num, target in links:
            links_checked += 1
            result = validate_relative_link(filepath, target, repo_root)

            if result:
                error_type, detail = result
                errors.append((rel_file, line_num, error_type, target, detail))

    # ---- GitHub Actions annotations ----
    for rel_path, line_num, error_type, target, detail in errors:
        # Forward-slash paths for GitHub annotations.
        gh_path = rel_path.replace(os.sep, "/")
        print(
            f"::error file={gh_path},line={line_num}::"
            f"[{error_type}] {detail}  (link target: {target})"
        )

    # ---- Summary ----
    print()
    print(f"Scanned {files_checked} file(s), checked {links_checked} link(s).")

    if errors:
        by_type: dict[str, int] = {}
        for _, _, t, _, _ in errors:
            by_type[t] = by_type.get(t, 0) + 1

        print(f"Found {len(errors)} broken link(s):")
        for t, c in sorted(by_type.items()):
            print(f"  {t}: {c}")

        # ---- GitHub Actions Job Summary ----
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## 🔗 Broken Markdown Links\n\n")
                sf.write(f"Scanned **{files_checked}** files, "
                         f"checked **{links_checked}** links, "
                         f"found **{len(errors)}** broken.\n\n")
                sf.write("| Type | File | Line | Link Target | Detail |\n")
                sf.write("|------|------|-----:|-------------|--------|\n")
                for rel_path, line_num, error_type, target, detail in errors:
                    gh_path = rel_path.replace(os.sep, "/")
                    # Escape pipes in target / detail for table cells.
                    safe_target = target.replace("|", "\\|")
                    safe_detail = detail.replace("|", "\\|")
                    sf.write(
                        f"| `{error_type}` "
                        f"| `{gh_path}` "
                        f"| {line_num} "
                        f"| `{safe_target}` "
                        f"| {safe_detail} |\n"
                    )

        sys.exit(1)
    else:
        print("All relative markdown links are valid. ✅")

        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## 🔗 Markdown Links\n\n")
                sf.write(f"Scanned **{files_checked}** files, "
                         f"checked **{links_checked}** links — "
                         f"all valid. ✅\n")

        sys.exit(0)


if __name__ == "__main__":
    main()
