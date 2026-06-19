#!/usr/bin/env python3
"""Validate Mermaid diagrams against the diagram standards rules.

Checks every Mermaid code block in .md files for:
  - backslash-n         : literal \\n in node/edge labels (use <br/> instead)
  - backslash-n-edge    : literal \\n in edge labels (|...\\n...|)
  - unquoted-br         : <br/> in node label without double quotes
  - double-curly        : {{ }} hexagon shape (breaks Jekyll Liquid)
  - theme-default       : theme: 'default' (must use theme: 'base')
  - gantt-min-suffix    : duration suffix 'min' in gantt (use 'm')
  - missing-init-block  : sequenceDiagram/gantt/timeline/xychart-beta without %%{init block
  - style-bad-text-color: text color not in approved set (#fff, #ccc, #aaa)
  - style-bad-fill      : fill color not in approved palette
  - style-missing-stroke: style statement without stroke: attribute
  - gantt-init-var      : gantt init block missing required theme variables
  - seq-init-var        : sequence init block missing required theme variables
  - timeline-init-var   : timeline init block missing required theme variables
  - xychart-init-var    : xychart init block missing required theme variables
  - er-missing-title    : erDiagram without YAML front matter title
  - er-paren-in-type    : erDiagram attribute type contains parentheses (use underscores)
  - er-unquoted-rel     : erDiagram relationship label not in double quotes

Usage:
  # Check specific files (one path per line on stdin):
  echo "path/to/file.md" | python check-mermaid-diagrams.py --stdin

  # Check all tracked .md files in a repo:
  python check-mermaid-diagrams.py [REPO_ROOT]

Exit code 0 = all diagrams valid, 1 = issues found.
"""

import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

EXCLUDED_DIRS = (
    os.path.join(".github", "instructions"),
    os.path.join(".github", "templates"),
    os.path.join(".github", "prompts"),
)

EXCLUDED_FILES: set[str] = {
    # Add relative paths of individual .md files that should be skipped by
    # the Mermaid checks, e.g. os.path.join("docs", "vendor-diagram.md").
}

# Diagram types that require a %%{init block for theming.
INIT_REQUIRED_TYPES = {"sequencediagram", "gantt", "timeline", "xychart-beta"}

# Approved fill colors from the diagram-standards instruction palette.
# Add more entries here if your diagram standard defines an extended palette.
APPROVED_FILLS = {
    # Core palette
    "#8b3a3a",   # Problem/Removed (Dark Red)
    "#2d5f2d",   # Success/Added (Dark Green)
    "#8b5a00",   # Warning/Changed (Dark Orange)
    "#1a4d7a",   # Info/Neutral (Dark Blue)
    "#3a3a3a",   # Inactive/Unused (Dark Gray)
    # Neutral greys
    "#555",      # Muted/secondary
    "#444",      # Disabled/Inactive
}

# Approved text colors for style statements.
# Core palette uses #fff; extended palette allows #ccc (reserved bits)
# and #aaa (disabled/inactive, muted context).
APPROVED_TEXT_COLORS = {"#fff", "#ffffff", "#ccc", "#cccccc", "#aaa", "#aaaaaa"}

# Diagram types where style statements are used.
# block-beta and stateDiagram don't use standard `style` statements the same way.
STYLE_CHECK_TYPES = {"graph", "flowchart"}

# Required gantt init-block theme variables.
GANTT_REQUIRED_VARS = {
    "taskbkgcolor", "taskbordercolor",
    "activetaskbkgcolor", "activetaskbordercolor",
    "critbkgcolor", "critbordercolor",
    "donetaskbkgcolor", "donetaskbordercolor",
    "sectionbkgcolor", "altsectionbkgcolor",
    "tasktextdarkcolor", "tasktextlightcolor",
    "tasktextoutsidecolor",
}

# Required sequence diagram init-block theme variables.
SEQ_REQUIRED_VARS = {
    "actorbkg", "actorborder", "actortextcolor",
    "signalcolor", "signaltextcolor",
}

# Required timeline init-block theme variables.
# Structural vars (always needed) + at least cScale0/cScaleLabel0.
TIMELINE_REQUIRED_VARS = {
    "titlecolor", "textcolor", "linecolor",
    "cscale0", "cscalelabel0",
}

# Required xychart-beta init-block theme variables.
XYCHART_REQUIRED_VARS = {
    "backgroundcolor",
    "titlecolor",
    "xaxislabelcolor", "xaxislinecolor",
    "yaxislabelcolor", "yaxislinecolor",
    "plotcolorpalette",
}



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _in_dir(rel_path: str, dirs: tuple[str, ...]) -> bool:
    return any(rel_path == d or rel_path.startswith(d + os.sep) for d in dirs)


def _is_excluded_file(rel_path: str) -> bool:
    return rel_path in EXCLUDED_FILES


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
            if _is_excluded_file(rel_os):
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
                    rel_file = os.path.join(rel, fname)
                    if _is_excluded_file(rel_file):
                        continue
                    yield rel_file


def extract_mermaid_blocks(lines: list[str]):
    """Yield (start_line_1based, end_line_1based, block_lines) for each
    fenced mermaid code block."""
    in_block = False
    block_start = 0
    block_lines: list[str] = []

    for idx, raw in enumerate(lines):
        stripped = raw.rstrip("\r\n")
        trimmed = stripped.lstrip()

        if not in_block:
            # Detect opening fence: ```mermaid (with optional leading spaces)
            if re.match(r"^(\s*)```\s*mermaid\s*$", stripped, re.IGNORECASE):
                in_block = True
                block_start = idx + 1  # 1-based
                block_lines = []
        else:
            # Detect closing fence
            if trimmed.startswith("```") and trimmed.rstrip("`").strip() == "":
                yield (block_start, idx + 1, block_lines)
                in_block = False
                block_lines = []
            else:
                block_lines.append(stripped)


def _diagram_type(block_lines: list[str]) -> str:
    """Return the lowercased diagram type keyword from the first
    non-init, non-blank, non-YAML-front-matter line."""
    in_yaml = False
    for line in block_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        if stripped == "---":
            in_yaml = not in_yaml
            continue
        if in_yaml:
            continue
        # First real word is the diagram type.
        return stripped.split()[0].lower()
    return ""


def _has_er_title(block_lines: list[str]) -> bool:
    """True if the ER diagram has a YAML front matter block with title."""
    in_yaml = False
    for line in block_lines:
        stripped = line.strip()
        if stripped == "---":
            if not in_yaml:
                in_yaml = True
            else:
                return False  # closed YAML without title
            continue
        if in_yaml and stripped.lower().startswith("title:"):
            return True
    return False


def _has_init_block(block_lines: list[str]) -> bool:
    """True if the block contains %%{init."""
    for line in block_lines:
        if "%%{init" in line:
            return True
    return False


# --- Individual checks ---------------------------------------------------

# Regex: node definitions with unquoted <br/> in labels.
# Mermaid node shapes open with various bracket combos:
#   [, [(, [(", [(", [", {, {", (, (", etc.
# The label is quoted when a " appears right before the text.
# We detect: NODEID + opening brackets + NO quote + content with <br/>.
_RE_NODE_UNQUOTED_BR = re.compile(
    r"""
    (?:^|\s|;)                   # start of line, whitespace, or semicolon
    [A-Za-z_][A-Za-z0-9_]*       # node ID
    [\[\(\{]+                    # one or more opening brackets
    (?!")                         # NOT followed by a double quote
    [^"\]\)\}\n]*               # label content (no quote, no close bracket)
    <br\s*/?>                     # contains <br/> or <br>
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Regex: literal \n inside node labels (single backslash + n).
# Must NOT match \\n (double backslash = escaped backslash in file paths).
_RE_BACKSLASH_N_LABEL = re.compile(
    r"""
    [A-Za-z_][A-Za-z0-9_]*      # node ID
    [\[\(\{]+                   # opening bracket(s)
    "?                           # optional opening quote
    [^"\}\]\)]*                 # label content
    (?<!\\)                     # not preceded by another backslash
    \\n                          # single backslash + n
    """,
    re.VERBOSE,
)

# Regex: {{ }} hexagon shape.
_RE_DOUBLE_CURLY = re.compile(r"\{\{[^}]*\}\}")

# Regex: theme: 'default' or theme:"default".
_RE_THEME_DEFAULT = re.compile(r"""theme\s*:\s*['"]default['"]""")

# Regex: gantt duration with 'min' suffix (e.g., 30min, 90min).
# Must appear after a comma in task metadata, not inside labels.
_RE_GANTT_MIN_SUFFIX = re.compile(r",\s*\d+min\b")

# Regex: style statement — extract fill and color values.
_RE_STYLE_FILL = re.compile(r"fill:\s*(#[0-9a-fA-F]{3,6})\b")
_RE_STYLE_COLOR = re.compile(r"(?<![a-z])color:\s*(#[0-9a-fA-F]{3,6})\b")
# Regex: literal \n inside edge labels: -->|...\n...|, -.->|...\n...|.
_RE_BACKSLASH_N_EDGE = re.compile(
    r"""
    \|             # opening pipe of edge label
    [^|]*          # label content
    (?<!\\)        # not preceded by another backslash
    \\n            # single backslash + n
    [^|]*          # rest of label
    \|             # closing pipe
    """,
    re.VERBOSE,
)


def _extract_init_vars(block_lines: list[str]) -> set[str]:
    """Extract all themeVariables key names from the %%{init block."""
    init_text = ""
    in_init = False
    for line in block_lines:
        if "%%{init" in line:
            in_init = True
        if in_init:
            init_text += line
            if "}%%" in line:
                break
    # Find all 'varName':'value' or "varName":"value" patterns.
    return {m.group(1).lower() for m in
            re.finditer(r"['\"](\w+)['\"]\s*:", init_text)}


def check_block(block_lines: list[str], block_start: int):
    """Return list of (line_1based, rule_id, detail) for a single block."""
    errors = []
    diagram_type = _diagram_type(block_lines)

    for offset, line in enumerate(block_lines):
        line_num = block_start + 1 + offset  # 1-based in original file
        stripped = line.strip()

        # Skip init directive lines and comments for most checks.
        if stripped.startswith("%%"):
            # But still check theme: 'default' inside init blocks.
            if _RE_THEME_DEFAULT.search(line):
                errors.append((
                    line_num,
                    "theme-default",
                    "Use theme: 'base' instead of theme: 'default'"
                ))
            continue

        # --- style statement checks ---
        if stripped.startswith("style "):
            if diagram_type in STYLE_CHECK_TYPES:
                # Check fill color is from approved palette.
                fill_match = _RE_STYLE_FILL.search(line)
                if fill_match:
                    fill_val = fill_match.group(1).lower()
                    if fill_val not in APPROVED_FILLS:
                        errors.append((
                            line_num,
                            "style-bad-fill",
                            f"Fill color {fill_val} is not in the "
                            f"approved palette"
                        ))

                # Check text color is from approved set.
                color_match = _RE_STYLE_COLOR.search(line)
                if color_match:
                    color_val = color_match.group(1).lower()
                    if color_val not in APPROVED_TEXT_COLORS:
                        errors.append((
                            line_num,
                            "style-bad-text-color",
                            f"Text color {color_val} is not in the "
                            f"approved set (#fff, #ccc, #aaa)"
                        ))
                elif "color:" not in line.lower():
                    errors.append((
                        line_num,
                        "style-bad-text-color",
                        "Style statement missing text color"
                    ))

                # Check stroke is present.
                if "stroke:" not in line.lower():
                    errors.append((
                        line_num,
                        "style-missing-stroke",
                        "Style statement missing stroke: attribute"
                    ))
            continue

        # Skip classDef lines.
        if stripped.startswith("classDef "):
            continue

        # --- backslash-n in labels ---
        if _RE_BACKSLASH_N_LABEL.search(line):
            errors.append((
                line_num,
                "backslash-n",
                "Literal \\n in label — use <br/> for line breaks"
            ))

        # --- backslash-n in edge labels ---
        if _RE_BACKSLASH_N_EDGE.search(line):
            errors.append((
                line_num,
                "backslash-n-edge",
                "Literal \\n in edge label — use <br/> for line "
                "breaks"
            ))

        # --- unquoted <br/> in node labels ---
        if _RE_NODE_UNQUOTED_BR.search(line):
            errors.append((
                line_num,
                "unquoted-br",
                "Node label with <br/> must be wrapped in double quotes"
            ))

        # --- double curly braces {{ }} ---
        if _RE_DOUBLE_CURLY.search(line):
            errors.append((
                line_num,
                "double-curly",
                "Hexagon shape {{ }} breaks Jekyll Liquid — use "
                "diamond { } or stadium ([ ]) instead"
            ))

        # --- gantt min suffix ---
        if diagram_type == "gantt" and _RE_GANTT_MIN_SUFFIX.search(line):
            errors.append((
                line_num,
                "gantt-min-suffix",
                "Duration suffix 'min' is invalid — use 'm' "
                "(e.g., 30m not 30min)"
            ))

    # --- Whole-block checks ---

    has_init = _has_init_block(block_lines)

    # Missing init block.
    if diagram_type in INIT_REQUIRED_TYPES and not has_init:
        errors.append((
            block_start + 1,
            "missing-init-block",
            f"{diagram_type} diagram should have a "
            f"%%{{init}} block for consistent theming"
        ))

    # Gantt init-block variable check.
    if diagram_type == "gantt" and has_init:
        init_vars = _extract_init_vars(block_lines)
        missing = GANTT_REQUIRED_VARS - init_vars
        if missing:
            errors.append((
                block_start + 1,
                "gantt-init-var",
                "Gantt init block missing theme variables: "
                + ", ".join(sorted(missing))
            ))

    # Sequence diagram init-block variable check.
    if diagram_type == "sequencediagram" and has_init:
        init_vars = _extract_init_vars(block_lines)
        missing = SEQ_REQUIRED_VARS - init_vars
        if missing:
            errors.append((
                block_start + 1,
                "seq-init-var",
                "Sequence diagram init block missing theme variables: "
                + ", ".join(sorted(missing))
            ))

    # Timeline init-block variable check.
    if diagram_type == "timeline" and has_init:
        init_vars = _extract_init_vars(block_lines)
        missing = TIMELINE_REQUIRED_VARS - init_vars
        if missing:
            errors.append((
                block_start + 1,
                "timeline-init-var",
                "Timeline init block missing theme variables: "
                + ", ".join(sorted(missing))
            ))

    # XY chart init-block variable check.
    if diagram_type == "xychart-beta" and has_init:
        init_vars = _extract_init_vars(block_lines)
        missing = XYCHART_REQUIRED_VARS - init_vars
        if missing:
            errors.append((
                block_start + 1,
                "xychart-init-var",
                "XY chart init block missing theme variables: "
                + ", ".join(sorted(missing))
            ))

    # ER diagram checks.
    if diagram_type == "erdiagram":
        # Must have YAML front matter with title.
        if not _has_er_title(block_lines):
            errors.append((
                block_start + 1,
                "er-missing-title",
                "erDiagram should have a YAML front matter block "
                "with title (e.g., title: Schema Name \u2014 db-name)"
            ))

        # Check attribute types for parentheses and unquoted relationship labels.
        in_entity = False
        for offset, line in enumerate(block_lines):
            line_num = block_start + 1 + offset
            stripped = line.strip()
            if stripped.startswith("%") or stripped == "---":
                continue
            if not stripped:
                continue
            # Skip YAML front matter content (title: lines).
            if stripped.lower().startswith("title:"):
                continue
            if stripped == "erDiagram" or stripped == "erdiagram":
                continue
            # Detect entity block: "EntityName {" at end of line.
            if stripped.endswith("{") and not any(
                op in stripped for op in (
                    "||--", "}o--", "|o--", "}|--"
                )
            ):
                in_entity = True
                continue
            if stripped == "}":
                in_entity = False
                continue
            # Inside entity: check attribute type for parentheses.
            if in_entity:
                if re.search(r"[()]", stripped):
                    errors.append((
                        line_num,
                        "er-paren-in-type",
                        "Attribute type contains parentheses \u2014 "
                        "use underscores (e.g., NVARCHAR_100 not "
                        "NVARCHAR(100))"
                    ))
            # Relationship lines: EntityA operator EntityB : "label"
            if not in_entity and ":" in stripped and any(
                op in stripped for op in (
                    "||--", "}o--", "|o--", "}|--"
                )
            ):
                rel_match = re.search(r":\s+(.+)$", stripped)
                if rel_match:
                    label = rel_match.group(1).strip()
                    if label and not (
                        label.startswith('"') and label.endswith('"')
                    ):
                        errors.append((
                            line_num,
                            "er-unquoted-rel",
                            "Relationship label should be in "
                            "double quotes"
                        ))

    return errors


def validate_file(filepath: str, repo_root: str):
    """Return list of (line_number, rule_id, detail) for all mermaid blocks."""
    full_path = os.path.join(repo_root, filepath)
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return [], 0

    all_errors = []
    block_count = 0

    for block_start, _block_end, block_lines in extract_mermaid_blocks(lines):
        block_count += 1
        all_errors.extend(check_block(block_lines, block_start))

    return all_errors, block_count


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
        input_text = sys.stdin.read()
        files = [f.strip() for f in input_text.splitlines() if f.strip()]
        files = [
            f for f in files
            if f.lower().endswith(".md")
            and not _in_dir(f.replace("/", os.sep), EXCLUDED_DIRS)
            and not _is_excluded_file(f.replace("/", os.sep))
        ]
    else:
        files = list(find_md_files(repo_root))

    all_errors: list[tuple[str, int, str, str]] = []
    files_checked = 0
    diagrams_checked = 0

    for rel_path in files:
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(full_path):
            continue

        files_checked += 1
        file_errors, block_count = validate_file(rel_path, repo_root)
        diagrams_checked += block_count

        for line_num, rule_id, detail in file_errors:
            all_errors.append((rel_path, line_num, rule_id, detail))

    is_ci = os.environ.get("CI") == "true"

    # ---- GitHub Actions annotations (CI only) ----
    if is_ci:
        for rel_path, line_num, rule_id, detail in all_errors:
            gh_path = rel_path.replace(os.sep, "/")
            print(
                f"::error file={gh_path},line={line_num}::"
                f"[{rule_id}] {detail}"
            )

    # ---- Console summary (always) ----
    print()
    print(f"Scanned {files_checked} file(s), "
          f"{diagrams_checked} Mermaid diagram(s).")

    if all_errors:
        by_type: dict[str, int] = {}
        for _, _, t, _ in all_errors:
            by_type[t] = by_type.get(t, 0) + 1

        print(f"Found {len(all_errors)} diagram issue(s):")
        for t, c in sorted(by_type.items()):
            print(f"  {t}: {c}")

        # Group by file.
        from collections import defaultdict
        by_file: dict[str, list] = defaultdict(list)
        for rel_path, line_num, rule_id, detail in all_errors:
            gh_path = rel_path.replace(os.sep, "/")
            by_file[gh_path].append((line_num, rule_id, detail))

        print()
        for filepath, issues in sorted(by_file.items()):
            print(f"  {filepath}")
            for line_num, rule_id, detail in issues:
                print(f"    Line {line_num}: [{rule_id}] {detail}")
            print()

        # ---- GitHub Actions Job Summary ----
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## 📐 Mermaid Diagram Issues\n\n")
                sf.write(f"Scanned **{files_checked}** files, "
                         f"**{diagrams_checked}** diagrams — "
                         f"found **{len(all_errors)}** issue(s).\n\n")
                sf.write("| Rule | File | Line | Detail |\n")
                sf.write("|------|------|-----:|--------|\n")
                for rel_path, line_num, rule_id, detail in all_errors:
                    gh_path = rel_path.replace(os.sep, "/")
                    safe = detail.replace("|", "\\|")
                    sf.write(
                        f"| `{rule_id}` "
                        f"| `{gh_path}` "
                        f"| {line_num} "
                        f"| {safe} |\n"
                    )

        sys.exit(1)
    else:
        print("All Mermaid diagrams are valid. ✅")

        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## 📐 Mermaid Diagrams\n\n")
                sf.write(f"Scanned **{files_checked}** files, "
                         f"**{diagrams_checked}** diagrams — "
                         f"all valid. ✅\n")

        sys.exit(0)


if __name__ == "__main__":
    main()
