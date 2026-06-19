#!/usr/bin/env python3
"""Validate markdown tables across the repository.

Checks every .md file for common table corruption issues:
  - empty-table       : header + separator with no data rows
  - column-mismatch   : data row has different column count than the header
  - no-blank-before   : no blank line before the table
  - no-blank-after    : no blank line after the table

Usage:
  # Check specific files (one path per line on stdin):
  echo "path/to/file.md" | python check-markdown-tables.py --stdin

  # Check all tracked .md files in a repo:
  python check-markdown-tables.py [REPO_ROOT]

Exit code 0 = all tables valid, 1 = issues found.
"""

import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Directories whose .md files are skipped entirely.
EXCLUDED_DIRS = (
    os.path.join(".github", "instructions"),
    os.path.join(".github", "templates"),
    os.path.join(".github", "prompts"),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _in_dir(rel_path: str, dirs: tuple[str, ...]) -> bool:
    """True if *rel_path* is inside any of *dirs*."""
    return any(rel_path == d or rel_path.startswith(d + os.sep) for d in dirs)


def find_md_files(repo_root: str):
    """Yield relative paths to tracked .md files, honoring exclusions."""
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
            if _in_dir(rel_os, EXCLUDED_DIRS):
                continue
            yield rel_os
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
                    yield os.path.join(rel, fname)


def is_separator_row(line: str) -> bool:
    """True if the line is a markdown table separator (e.g., |---|---|---|)."""
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return False
    inner = stripped[1:-1]
    # Each cell must contain only dashes, colons, and spaces.
    cells = inner.split("|")
    return all(re.fullmatch(r"\s*:?-+:?\s*", cell) for cell in cells)


def count_columns(line: str) -> int:
    """Count the number of columns in a table row.

    Handles escaped pipes (&#124;) by replacing them before counting.
    """
    # Replace escaped pipes so they don't count as separators.
    # Handle backslash-pipe (kramdown escape) and HTML entity.
    cleaned = line.replace("\\|", "\x00").replace("&#124;", "\x00")
    stripped = cleaned.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return 0
    inner = stripped[1:-1]
    return inner.count("|") + 1


def is_table_row(line: str) -> bool:
    """True if the line looks like a markdown table row."""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 1


def validate_tables(filepath: str, repo_root: str):
    """Return list of (line_number, error_type, detail) for table issues."""
    full_path = os.path.join(repo_root, filepath)
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return []

    errors = []
    in_code_block = False
    in_html_comment = False

    # Track table state.
    table_start = None       # Line number of the header row (1-based).
    header_cols = 0           # Column count from the header.
    has_separator = False     # Whether we've seen the separator row.
    has_data_row = False      # Whether we've seen at least one data row.

    def _end_table(line_idx: int):
        """Called when the table ends (non-table line encountered)."""
        nonlocal table_start, header_cols, has_separator, has_data_row
        if table_start is not None and has_separator:
            # Check: empty table (no data rows).
            if not has_data_row:
                errors.append((
                    table_start,
                    "empty-table",
                    "Table has header and separator but no data rows"
                ))

            # Check: no blank line after table.
            # line_idx is the current (0-based) index of the first non-table line.
            if line_idx < len(lines):
                after_line = lines[line_idx].rstrip("\r\n")
                # Blank line or end-of-file is fine.
                if after_line.strip() != "":
                    errors.append((
                        line_idx + 1,
                        "no-blank-after",
                        "No blank line after table (table started at line "
                        f"{table_start})"
                    ))

        table_start = None
        header_cols = 0
        has_separator = False
        has_data_row = False

    for idx, raw_line in enumerate(lines):
        line = raw_line.rstrip("\r\n")
        stripped = line.strip()

        # --- Fenced code block toggle ---
        if not in_html_comment and (
            stripped.startswith("```") or stripped.startswith("~~~")
        ):
            if in_code_block:
                in_code_block = False
            else:
                _end_table(idx)
                in_code_block = True
            continue
        if in_code_block:
            continue

        # --- HTML comment handling ---
        if in_html_comment:
            if "-->" in line:
                in_html_comment = False
            continue

        if "<!--" in stripped and "-->" not in stripped:
            _end_table(idx)
            in_html_comment = True
            continue

        # --- Table row detection ---
        if is_table_row(line):
            if table_start is None:
                # Potential header row — start tracking.
                table_start = idx + 1
                header_cols = count_columns(line)
                has_separator = False
                has_data_row = False

                # Check: no blank line before table.
                if idx > 0:
                    before_line = lines[idx - 1].rstrip("\r\n")
                    if before_line.strip() != "":
                        errors.append((
                            idx + 1,
                            "no-blank-before",
                            "No blank line before table"
                        ))
            elif not has_separator:
                # Should be the separator row.
                if is_separator_row(line):
                    has_separator = True
                else:
                    # Not a valid table — reset.
                    _end_table(idx)
            else:
                # Data row — check column count.
                has_data_row = True
                row_cols = count_columns(line)
                if row_cols != header_cols:
                    # Allow section header rows: a single-column row in a
                    # multi-column table is a common visual grouping hack
                    # that renders correctly in most markdown renderers.
                    if row_cols == 1 and header_cols > 1:
                        pass  # intentional section header — not an error
                    else:
                        errors.append((
                            idx + 1,
                            "column-mismatch",
                            f"Row has {row_cols} column(s), header has "
                            f"{header_cols} (table started at line "
                            f"{table_start})"
                        ))
        else:
            # Non-table line — end any open table.
            _end_table(idx)

    # Handle table at end of file.
    _end_table(len(lines))

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Ensure UTF-8 output.
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")

    use_stdin = "--stdin" in sys.argv
    repo_root = os.path.abspath(".")

    # Determine which arg (if any) is the repo root.
    for arg in sys.argv[1:]:
        if arg != "--stdin":
            repo_root = os.path.abspath(arg)
            break

    if use_stdin:
        # Read file list from stdin (one path per line).
        input_text = sys.stdin.read()
        files = [f.strip() for f in input_text.splitlines() if f.strip()]
        # Filter excluded dirs and non-.md files.
        files = [
            f for f in files
            if f.lower().endswith(".md")
            and not _in_dir(f.replace("/", os.sep), EXCLUDED_DIRS)
        ]
    else:
        files = list(find_md_files(repo_root))

    all_errors: list[tuple[str, int, str, str]] = []
    files_checked = 0
    tables_checked = 0

    for rel_path in files:
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(full_path):
            continue

        files_checked += 1
        file_errors = validate_tables(rel_path, repo_root)

        if file_errors:
            tables_checked += len(file_errors)
            for line_num, error_type, detail in file_errors:
                all_errors.append((rel_path, line_num, error_type, detail))

    is_ci = os.environ.get("CI") == "true"

    # ---- GitHub Actions annotations (CI only) ----
    if is_ci:
        for rel_path, line_num, error_type, detail in all_errors:
            gh_path = rel_path.replace(os.sep, "/")
            print(
                f"::error file={gh_path},line={line_num}::"
                f"[{error_type}] {detail}"
            )

    # ---- Console summary (always) ----
    print()
    print(f"Scanned {files_checked} file(s).")

    if all_errors:
        by_type: dict[str, int] = {}
        for _, _, t, _ in all_errors:
            by_type[t] = by_type.get(t, 0) + 1

        print(f"Found {len(all_errors)} table issue(s):")
        for t, c in sorted(by_type.items()):
            print(f"  {t}: {c}")

        # Group errors by file for clear reading.
        from collections import defaultdict
        by_file: dict[str, list] = defaultdict(list)
        for rel_path, line_num, error_type, detail in all_errors:
            gh_path = rel_path.replace(os.sep, "/")
            by_file[gh_path].append((line_num, error_type, detail))

        print()
        for filepath, issues in sorted(by_file.items()):
            print(f"  {filepath}")
            for line_num, error_type, detail in issues:
                print(f"    Line {line_num}: [{error_type}] {detail}")
            print()

        # ---- GitHub Actions Job Summary ----
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## 📊 Markdown Table Issues\n\n")
                sf.write(f"Scanned **{files_checked}** files, "
                         f"found **{len(all_errors)}** issue(s).\n\n")
                sf.write("| Type | File | Line | Detail |\n")
                sf.write("|------|------|-----:|--------|\n")
                for rel_path, line_num, error_type, detail in all_errors:
                    gh_path = rel_path.replace(os.sep, "/")
                    safe_detail = detail.replace("|", "\\|")
                    sf.write(
                        f"| `{error_type}` "
                        f"| `{gh_path}` "
                        f"| {line_num} "
                        f"| {safe_detail} |\n"
                    )

        sys.exit(1)
    else:
        print("All markdown tables are valid. ✅")

        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## 📊 Markdown Tables\n\n")
                sf.write(f"Scanned **{files_checked}** files — "
                         f"all tables valid. ✅\n")

        sys.exit(0)


if __name__ == "__main__":
    main()
