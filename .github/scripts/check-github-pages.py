#!/usr/bin/env python3
"""Comprehensive GitHub Pages validation for the site.

Builds a complete site map from ALL published .md files, then validates
structural, hierarchy, and content rules that require full context.

Error checks (fail the build):
  front-matter-missing      : File has no YAML front matter
  title-missing             : No `title` in front matter
  parent-not-found          : `parent` matches no page's title
  grand-parent-missing      : Parent title is non-unique; grand_parent required
  grand-parent-not-found    : grand_parent + parent combo matches no page
  grand-parent-mismatch     : grand_parent does not match resolved parent's parent
  duplicate-sibling-title   : Two pages under the same parent share a title
  kebab-case-violation      : File or folder name not lowercase kebab-case
  permalink-misuse          : `permalink` used on a non-root file
  mermaid-double-braces     : {{ }} in Mermaid block (breaks Jekyll Liquid)

Warning checks (reported but do not fail unless --warnings-as-errors):
  title-not-quoted          : Title not double-quoted (YAML safety)
  display-math-no-blank     : $$ display math without surrounding blank lines
  manual-navigation         : Manual back-link or navigation section detected

Always runs a FULL SCAN — hierarchy rules require complete context across
all pages and cannot work on deltas alone.

Usage:
  python check-github-pages.py [REPO_ROOT]
  python check-github-pages.py --warnings-as-errors [REPO_ROOT]

Exit code 0 = pass (or only warnings), 1 = errors found.
"""

import os
import re
import subprocess
import sys
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

# Directories excluded from scanning (not published as GitHub Pages).
EXCLUDED_DIRS = (
    ".github",
)

# Files exempt from kebab-case naming check.
KEBAB_EXEMPT_NAMES = frozenset({"README.md"})

# Path segments starting with these prefixes skip kebab-case check.
KEBAB_EXEMPT_PREFIXES = ("_", ".")

# Valid kebab-case: lowercase alphanumeric segments separated by hyphens
# or dots (dots for version numbers like 5.0.0 and file extensions .md).
KEBAB_RE = re.compile(r"^[a-z0-9]+([-.][a-z0-9]+)*$")

# Patterns that indicate manual navigation (violates just-the-docs rules).
MANUAL_NAV_PATTERNS = [
    re.compile(r"\[←\s*(Back|Home|All\s|Return)", re.IGNORECASE),
    re.compile(r">\s*\*\*Navigation", re.IGNORECASE),
    re.compile(r"\[Back to\s", re.IGNORECASE),
]

# Check types that are warnings (do not fail the build by default).
# Everything not in this set is an error.
WARNING_TYPES = frozenset({
    "title-not-quoted",
    "display-math-no-blank",
    "manual-navigation",
})


# ═══════════════════════════════════════════════════════════════════════════
# File discovery
# ═══════════════════════════════════════════════════════════════════════════

def _in_excluded_dir(rel_path):
    """True if *rel_path* is inside an excluded directory."""
    norm = rel_path.replace(os.sep, "/")
    return any(norm == d or norm.startswith(d + "/") for d in EXCLUDED_DIRS)


def find_md_files(repo_root):
    """Yield relative paths of tracked .md files, excluding non-page dirs.

    Uses ``git ls-files`` so gitignored files are excluded automatically.
    Falls back to filesystem walk when git is unavailable.
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
        paths = None

    if paths is not None:
        for rel in paths:
            rel_os = rel.replace("/", os.sep)
            if not _in_excluded_dir(rel):
                yield rel_os
    else:
        # Fallback: walk the filesystem.
        for dirpath, dirnames, filenames in os.walk(repo_root):
            rel = os.path.relpath(dirpath, repo_root)
            if rel == ".":
                rel = ""
            if _in_excluded_dir(rel):
                dirnames.clear()
                continue
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".")
            ]
            for fname in filenames:
                if fname.lower().endswith(".md"):
                    frel = os.path.join(rel, fname) if rel else fname
                    yield frel


# ═══════════════════════════════════════════════════════════════════════════
# Front-matter parsing
# ═══════════════════════════════════════════════════════════════════════════

def _unquote(value):
    """Remove surrounding YAML quotes from a scalar value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _strip_emoji_prefix(text):
    """Strip leading emoji characters from heading text.

    Skips any non-ASCII characters (emoji, variation selectors, ZWJ) and
    whitespace at the start, returning the remaining text.
    """
    text = text.strip()
    if not text:
        return text
    # If first char is ASCII printable (not space), there is no emoji prefix.
    if text[0].isascii() and not text[0].isspace():
        return text
    for i, ch in enumerate(text):
        if ch.isascii() and not ch.isspace():
            return text[i:].strip()
    return text


def _find_h1(lines, start):
    """Find the first H1 heading starting from *start*, skipping code blocks.

    Returns the heading text with emoji prefix stripped, or None.
    """
    in_code = False
    for i in range(start, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^#\s+(.+)$", lines[i])
        if m:
            return _strip_emoji_prefix(m.group(1).strip())
    return None


def parse_page(rel_path, repo_root):
    """Parse YAML front matter and first H1 from a markdown file.

    Returns a dict with: path, has_fm, title, raw_title, parent,
    raw_parent, grand_parent, raw_grand_parent, nav_exclude, permalink, h1.
    """
    page = {
        "path": rel_path,
        "has_fm": False,
        "title": None,
        "raw_title": None,
        "parent": None,
        "raw_parent": None,
        "grand_parent": None,
        "raw_grand_parent": None,
        "nav_exclude": False,
        "permalink": None,
        "h1": None,
    }

    full_path = os.path.join(repo_root, rel_path)
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as fh:
            raw_lines = fh.readlines()
    except OSError:
        return page

    lines = [l.rstrip("\r\n") for l in raw_lines]

    # --- Front matter ---
    if not lines or lines[0] != "---":
        page["h1"] = _find_h1(lines, 0)
        return page

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i] == "---":
            end_idx = i
            break

    if end_idx is None:
        page["h1"] = _find_h1(lines, 0)
        return page

    page["has_fm"] = True

    for line in lines[1:end_idx]:
        m = re.match(r"^([\w][\w-]*)\s*:\s*(.+)$", line)
        if not m:
            continue
        key, raw_val = m.group(1), m.group(2).strip()
        val = _unquote(raw_val)

        if key == "title":
            page["raw_title"] = raw_val
            page["title"] = val
        elif key == "parent":
            page["raw_parent"] = raw_val
            page["parent"] = val
        elif key == "grand_parent":
            page["raw_grand_parent"] = raw_val
            page["grand_parent"] = val
        elif key == "nav_exclude" and val.lower() == "true":
            page["nav_exclude"] = True
        elif key == "permalink":
            page["permalink"] = val

    page["h1"] = _find_h1(lines, end_idx + 1)
    return page


# ═══════════════════════════════════════════════════════════════════════════
# Per-file checks
# ═══════════════════════════════════════════════════════════════════════════

def check_front_matter(page):
    """Validate front-matter structural rules for one page."""
    errors = []
    rel = page["path"]

    if not page["has_fm"]:
        errors.append((rel, 1, "front-matter-missing",
                       "File has no YAML front matter"))
        return errors  # Everything else requires front matter.

    # --- title required ---
    if not page["title"]:
        errors.append((rel, 1, "title-missing",
                       "Front matter has no title field"))
    else:
        # title must be double-quoted.
        raw = page["raw_title"]
        if not (raw.startswith('"') and raw.endswith('"')):
            errors.append((rel, 1, "title-not-quoted",
                           f"title: {raw} — must be double-quoted"))

    # --- permalink only on root ---
    if page["permalink"]:
        norm = page["path"].replace(os.sep, "/")
        if norm != "README.md":
            errors.append((rel, 1, "permalink-misuse",
                           "permalink should only appear on the root README.md"))

    return errors


def check_kebab_case_all(pages):
    """Check kebab-case naming across all file paths (deduplicated)."""
    errors = []
    seen_bad = set()

    for page in pages:
        parts = page["path"].replace(os.sep, "/").split("/")
        for part in parts:
            if part in KEBAB_EXEMPT_NAMES:
                continue
            if any(part.startswith(p) for p in KEBAB_EXEMPT_PREFIXES):
                continue
            if part in seen_bad:
                continue
            if not KEBAB_RE.fullmatch(part):
                seen_bad.add(part)
                errors.append((
                    page["path"], 1, "kebab-case-violation",
                    f"\"{part}\" is not lowercase kebab-case"
                ))

    return errors


def check_content(rel_path, repo_root):
    """Check content rules: Mermaid double braces, display math blank
    lines, and manual navigation patterns."""
    full_path = os.path.join(repo_root, rel_path)
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return []

    errors = []
    in_front_matter = False
    in_code_block = False
    in_mermaid = False
    display_math_open = None  # Line number of opening $$, or None.

    for idx, raw in enumerate(lines):
        line = raw.rstrip("\r\n")
        stripped = line.strip()
        ln = idx + 1  # 1-based line number.

        # --- Skip front matter ---
        if idx == 0 and stripped == "---":
            in_front_matter = True
            continue
        if in_front_matter:
            if stripped == "---":
                in_front_matter = False
            continue

        # --- Code block toggling ---
        if stripped.startswith("```") or stripped.startswith("~~~"):
            if in_code_block:
                in_code_block = False
                in_mermaid = False
            else:
                in_code_block = True
                in_mermaid = "mermaid" in stripped.lower()
            continue

        # --- Mermaid {{ }} check ---
        if in_mermaid and "{{" in line:
            errors.append((
                rel_path, ln, "mermaid-double-braces",
                "{{ }} breaks Jekyll Liquid — use { } (diamond) "
                "or ([ ]) (stadium) instead"
            ))

        if in_code_block:
            continue

        # --- Display math $$ blank lines ---
        is_single = (
            stripped.startswith("$$")
            and stripped.endswith("$$")
            and len(stripped) > 2
        )
        is_bare_dollar = stripped == "$$"

        if is_single:
            # Single-line display math: $$ expression $$.
            if idx > 0 and lines[idx - 1].rstrip("\r\n").strip():
                errors.append((
                    rel_path, ln, "display-math-no-blank",
                    "$$ display math needs a blank line before"
                ))
            if idx + 1 < len(lines) and lines[idx + 1].rstrip("\r\n").strip():
                errors.append((
                    rel_path, ln, "display-math-no-blank",
                    "$$ display math needs a blank line after"
                ))
        elif is_bare_dollar:
            if display_math_open is None:
                # Opening $$.
                display_math_open = ln
                if idx > 0 and lines[idx - 1].rstrip("\r\n").strip():
                    errors.append((
                        rel_path, ln, "display-math-no-blank",
                        "$$ display math needs a blank line before"
                    ))
            else:
                # Closing $$.
                display_math_open = None
                if (idx + 1 < len(lines)
                        and lines[idx + 1].rstrip("\r\n").strip()):
                    errors.append((
                        rel_path, ln, "display-math-no-blank",
                        "$$ display math needs a blank line after"
                    ))

        # --- Manual navigation ---
        for pat in MANUAL_NAV_PATTERNS:
            if pat.search(line):
                errors.append((
                    rel_path, ln, "manual-navigation",
                    "Manual navigation detected — sidebar and breadcrumbs "
                    "are generated automatically by just-the-docs"
                ))
                break  # One error per line is enough.

    return errors


# ═══════════════════════════════════════════════════════════════════════════
# Cross-file hierarchy checks
# ═══════════════════════════════════════════════════════════════════════════

def validate_hierarchy(pages):
    """Validate parent/grand_parent chains and sibling title uniqueness.

    Requires the complete site map — cannot work on deltas because valid
    parent resolution depends on knowing ALL titles in the site.
    """
    errors = []

    # Build title → pages lookup.
    title_map = defaultdict(list)
    for p in pages:
        if p["has_fm"] and p["title"]:
            title_map[p["title"]].append(p)

    # Track children grouped by resolved parent (path → list of children).
    siblings = defaultdict(list)

    for page in pages:
        if not page["has_fm"] or not page["title"]:
            continue

        parent_val = page["parent"]
        if not parent_val:
            # Root-level page — track for sibling uniqueness.
            siblings["__ROOT__"].append(page)
            continue

        candidates = title_map.get(parent_val, [])

        if not candidates:
            errors.append((
                page["path"], 1, "parent-not-found",
                f"parent: \"{parent_val}\" — no page has this title"
            ))
            continue

        resolved = None

        if len(candidates) == 1:
            # Unambiguous parent.
            resolved = candidates[0]
            # If grand_parent is set, verify it matches the parent's parent.
            if page["grand_parent"]:
                actual_gp = resolved.get("parent")
                if actual_gp != page["grand_parent"]:
                    errors.append((
                        page["path"], 1, "grand-parent-mismatch",
                        f"grand_parent: \"{page['grand_parent']}\" but "
                        f"resolved parent's parent is "
                        f"\"{actual_gp or '(none)'}\""
                    ))
        else:
            # Multiple pages share the parent title — disambiguation needed.
            if not page["grand_parent"]:
                titles_at = [
                    c["path"].replace(os.sep, "/") for c in candidates
                ]
                errors.append((
                    page["path"], 1, "grand-parent-missing",
                    f"parent: \"{parent_val}\" matches {len(candidates)} "
                    f"pages — grand_parent required to disambiguate "
                    f"({', '.join(titles_at)})"
                ))
            else:
                # Filter candidates by grand_parent.
                matches = [
                    c for c in candidates
                    if c.get("parent") == page["grand_parent"]
                ]
                if not matches:
                    errors.append((
                        page["path"], 1, "grand-parent-not-found",
                        f"No page titled \"{parent_val}\" has parent "
                        f"\"{page['grand_parent']}\""
                    ))
                elif len(matches) > 1:
                    errors.append((
                        page["path"], 1, "grand-parent-ambiguous",
                        f"Multiple pages titled \"{parent_val}\" with parent "
                        f"\"{page['grand_parent']}\" — suffix needed"
                    ))
                else:
                    resolved = matches[0]

        if resolved:
            siblings[resolved["path"]].append(page)

    # --- Duplicate sibling titles ---
    for parent_key, children in siblings.items():
        by_title = defaultdict(list)
        for child in children:
            if child["title"]:
                by_title[child["title"]].append(child)

        for title, dupes in by_title.items():
            if len(dupes) > 1:
                all_paths = [
                    d["path"].replace(os.sep, "/") for d in dupes
                ]
                for dupe in dupes[1:]:
                    others = [
                        p for p in all_paths
                        if p != dupe["path"].replace(os.sep, "/")
                    ]
                    display_parent = (
                        parent_key.replace(os.sep, "/")
                        if parent_key != "__ROOT__"
                        else "(root level)"
                    )
                    errors.append((
                        dupe["path"], 1, "duplicate-sibling-title",
                        f"title \"{title}\" duplicated under parent "
                        f"\"{display_parent}\"; see also: "
                        f"{', '.join(others)}"
                    ))

    return errors


# ═══════════════════════════════════════════════════════════════════════════
# Reporting
# ═══════════════════════════════════════════════════════════════════════════

def report(all_issues, files_checked, warnings_as_errors=False):
    """Print results to console, emit GitHub annotations, and write
    the job summary.  Returns the process exit code (0 or 1).

    Issues whose type is in WARNING_TYPES are treated as warnings and
    do not affect the exit code unless *warnings_as_errors* is True.
    """
    is_ci = os.environ.get("CI") == "true"

    # Sort for deterministic output.
    all_issues.sort(key=lambda e: (e[0], e[1], e[2]))

    # Separate errors from warnings.
    errors = [i for i in all_issues if i[2] not in WARNING_TYPES]
    warnings = [i for i in all_issues if i[2] in WARNING_TYPES]

    if warnings_as_errors:
        errors = all_issues
        warnings = []

    # ── GitHub Actions file annotations ──
    if is_ci:
        for rel_path, ln, etype, detail in errors:
            gh = rel_path.replace(os.sep, "/")
            print(
                f"::error file={gh},line={ln}::"
                f"[{etype}] {detail}"
            )
        for rel_path, ln, etype, detail in warnings:
            gh = rel_path.replace(os.sep, "/")
            print(
                f"::warning file={gh},line={ln}::"
                f"[{etype}] {detail}"
            )

    # ── Console summary ──
    print()
    print(f"Scanned {files_checked} file(s) (full scan).")

    if errors or warnings:
        by_type = defaultdict(int)
        for _, _, t, _ in all_issues:
            by_type[t] += 1

        if errors:
            print(f"Found {len(errors)} error(s):")
            for t, c in sorted(by_type.items()):
                if t not in WARNING_TYPES or warnings_as_errors:
                    print(f"  {t}: {c}")

        if warnings:
            print(f"Found {len(warnings)} warning(s):")
            for t, c in sorted(by_type.items()):
                if t in WARNING_TYPES:
                    print(f"  {t}: {c}")

        # Group by file for readable output.
        by_file = defaultdict(list)
        for rel_path, ln, etype, detail in all_issues:
            gh = rel_path.replace(os.sep, "/")
            severity = "warning" if etype in WARNING_TYPES and not warnings_as_errors else "error"
            by_file[gh].append((ln, etype, detail, severity))

        print()
        for filepath in sorted(by_file):
            print(f"  {filepath}")
            for ln, etype, detail, severity in by_file[filepath]:
                tag = "⚠" if severity == "warning" else "✖"
                print(f"    {tag} Line {ln}: [{etype}] {detail}")
            print()

        # ── GitHub Actions Job Summary ──
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## 📋 GitHub Pages Validation\n\n")
                sf.write(
                    f"Scanned **{files_checked}** files (full scan) — "
                    f"**{len(errors)}** error(s), "
                    f"**{len(warnings)}** warning(s).\n\n"
                )
                if errors:
                    sf.write("### Errors\n\n")
                    sf.write("| Type | File | Line | Detail |\n")
                    sf.write("|------|------|-----:|--------|\n")
                    for rel_path, ln, etype, detail in errors:
                        gh = rel_path.replace(os.sep, "/")
                        safe = detail.replace("|", "\\|")
                        sf.write(
                            f"| `{etype}` | `{gh}` | {ln} | {safe} |\n"
                        )
                    sf.write("\n")
                if warnings:
                    sf.write("### Warnings\n\n")
                    sf.write("| Type | File | Line | Detail |\n")
                    sf.write("|------|------|-----:|--------|\n")
                    for rel_path, ln, etype, detail in warnings:
                        gh = rel_path.replace(os.sep, "/")
                        safe = detail.replace("|", "\\|")
                        sf.write(
                            f"| `{etype}` | `{gh}` | {ln} | {safe} |\n"
                        )

        return 1 if errors else 0

    print("All GitHub Pages rules passed. ✅")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as sf:
            sf.write("## 📋 GitHub Pages Validation\n\n")
            sf.write(
                f"Scanned **{files_checked}** files (full scan) — "
                f"all rules passed. ✅\n"
            )

    return 0


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")

    warnings_as_errors = "--warnings-as-errors" in sys.argv
    repo_root = os.path.abspath(".")
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            repo_root = os.path.abspath(arg)
            break

    # ── Phase 1: Discover and parse all pages ──
    files = list(find_md_files(repo_root))
    pages = [parse_page(f, repo_root) for f in files]

    all_issues = []

    # ── Phase 2: Per-file checks ──
    for page in pages:
        all_issues.extend(check_front_matter(page))
        all_issues.extend(check_content(page["path"], repo_root))

    # Kebab-case naming (deduplicated across files).
    all_issues.extend(check_kebab_case_all(pages))

    # ── Phase 3: Cross-file hierarchy checks ──
    all_issues.extend(validate_hierarchy(pages))

    # ── Phase 4: Report ──
    exit_code = report(all_issues, len(files), warnings_as_errors)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
