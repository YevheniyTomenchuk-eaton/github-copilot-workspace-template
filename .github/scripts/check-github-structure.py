#!/usr/bin/env python3
"""Validate .github/ folder structure against project conventions.

Checks that instruction, skill, template, and hook files follow the naming
conventions and mirror the main project folder structure.

Checks performed:
  - instruction-filename-mismatch : stem doesn't match directory path
  - instruction-missing-applyto   : missing applyTo frontmatter
  - prompt-file-retired           : a prompt artifact was reintroduced —
                                    prompts are retired, use a skill instead
  - template-filename-mismatch    : prefix doesn't match directory path
  - hook-filename-mismatch        : hook stem doesn't match directory path
  - hook-missing-hooks-key        : hook JSON missing top-level 'hooks' object
  - hook-invalid-json             : hook file is not valid JSON
  - hook-unknown-event            : hook references an unknown event name
  - agent-missing-name            : agent file missing 'name' frontmatter
  - agent-missing-description     : agent file missing 'description' frontmatter
  - agent-name-mismatch           : agent 'name' != filename stem (dotted folder path)
  - agent-has-model               : agent file sets a forbidden 'model' key
  - leading-fence-wrapper         : file starts with a code fence (```prompt,
                                    ````instructions, …) that wraps the whole
                                    file and hides its YAML frontmatter
  - skill-missing-file            : skill folder missing SKILL.md
  - skill-missing-name            : SKILL.md missing 'name' frontmatter
  - skill-missing-description     : SKILL.md missing 'description' frontmatter
  - stem-deeper-than-dir          : stem encodes deeper path than its location;
                                    file should be moved to the matching subdir
  - wrong-suffix                  : unexpected file suffix for its location
  - duplicate-suffix              : suffix keyword repeated in filename
                                    (e.g. a.template.b.template.md)
  - stem-contains-suffix-keyword  : stem encodes a path segment that duplicates
                                    the suffix keyword (deduplication rule)
  - consecutive-duplicate-segment  : same word appears in two or more
                                    consecutive dot-segments (e.g. diagram.diagram)
  - not-kebab-case                : filename or component not lowercase kebab-case
  - misplaced-file                : .instructions.md / .prompt.md / .template.*
                                    file found outside .github/
  - mirror-orphan-subdir          : subdir under .github/{type}/ has no
                                    matching project folder

Usage:
  python check-github-structure.py [REPO_ROOT]            # full scan
  echo "file1\nfile2" | python check-github-structure.py --stdin  # delta scan

In delta mode (--stdin) only the listed files are checked for per-file
validation; the mirror-orphan-subdir check still runs (it uses directory
context, not individual file content).

Exit code 0 = all checks pass, 1 = issues found.
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# The mirrored sub-trees inside .github/ whose subfolders must map 1:1 to a
# project folder (instructions, templates, and hooks all mirror the location of
# the thing they govern).
MIRROR_TYPES = ("instructions", "templates", "hooks")

# Prompts are retired: every /command is a skill under .github/skills/.
PROMPT_RETIRED_DETAIL = (
    "Prompts are retired — this repository has standardized on skills. "
    "Create .github/skills/<name>/SKILL.md instead (invoked as /<name> exactly "
    "like a prompt). See the github-conventions skill."
)

# Event names recognised by VS Code's agent hooks (Preview). A committed hook
# JSON keys its command arrays by these event names. VS Code accepts both its
# native PascalCase keys and the Copilot CLI lowerCamelCase form (which it
# converts to PascalCase on load) — the /hooks UI emits camelCase for the newer
# SessionEnd / ErrorOccurred events, so both casings are valid on disk.
_HOOK_EVENT_NAMES = (
    "SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse",
    "PreCompact", "SubagentStart", "SubagentStop", "Stop",
    "SessionEnd", "ErrorOccurred",
)
_HOOK_EVENTS = frozenset(
    set(_HOOK_EVENT_NAMES)
    | {name[0].lower() + name[1:] for name in _HOOK_EVENT_NAMES}
)

# Directories that exist in .github/{type}/ as organisational grouping
# but don't map 1:1 to a project folder at that exact path.
# key = relative path under .github/{type}/, value = reason
KNOWN_ORGANISATIONAL_DIRS: dict[str, str] = {
    # Add entries here for any .github/{type}/ subdirectory that groups files
    # organisationally but does not map 1:1 to a tracked project folder at that
    # exact path. key = relative path under .github/{type}/, value = reason.
    # Example:
    #   "sources": "gitignored folder — not a tracked content folder",
}

# Instruction files whose stem is allowed to NOT match the directory path.
# key = relative path under .github/instructions/, value = reason
#
# Normal rule: stem must exactly equal dir_to_stem(directory) or
# dir_to_stem(directory).{descriptor}.
# These exceptions have stems that skip or abbreviate path segments.
KNOWN_INSTRUCTION_EXCEPTIONS: dict[str, str] = {
    # Root-level global instructions (applyTo: "**") use descriptive names
    # instead of a path-mirroring stem. Add your own global instructions here.
    "diagram-standards.instructions.md": "global instruction with descriptive name",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def dir_to_stem(rel_dir: str) -> str:
    """Convert a relative directory path to dot-joined stem.

    Example: 'foundation/databases' -> 'foundation.databases'
    """
    if not rel_dir or rel_dir == ".":
        return ""
    parts = rel_dir.replace(os.sep, "/").strip("/").split("/")
    return ".".join(parts)


def parse_frontmatter(filepath: str) -> dict[str, str]:
    """Extract YAML front matter key-value pairs (simple single-line only).

    Handles VS Code instruction/prompt wrappers: files may start with
    a fenced code marker (e.g. ```prompt or ````instructions) before
    the --- frontmatter block.
    """
    result: dict[str, str] = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return result

    if not lines:
        return result

    # Skip optional leading fenced-code wrapper (```prompt, ````instructions, etc.)
    start = 0
    first = lines[0].rstrip("\r\n").strip()
    if first.startswith("```") and first != "---":
        start = 1

    if start >= len(lines) or lines[start].rstrip("\r\n").strip() != "---":
        return result

    for line in lines[start + 1:]:
        stripped = line.rstrip("\r\n").strip()
        if stripped == "---":
            break
        m = re.match(r'^(\w[\w-]*):\s*(?:"([^"]*)"|\'([^\']*)\'|(.+))$', stripped)
        if m:
            key = m.group(1)
            value = m.group(2) if m.group(2) is not None else (
                m.group(3) if m.group(3) is not None else m.group(4).strip()
            )
            result[key] = value

    return result


def starts_with_fence(filepath: str) -> str | None:
    """Return the offending fence line if the file's first non-blank line is a
    code fence (``` or ~~~), else None.

    A customization file must begin with its YAML front matter; wrapping the
    whole file in a fenced-code block hides the frontmatter from the VS Code
    loader so the instruction/prompt never activates.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("```") or stripped.startswith("~~~"):
                    return stripped
                return None
    except OSError:
        return None
    return None


def get_project_dirs(repo_root: str) -> set[str]:
    """Return set of all directory paths (relative) in the main project.

    Excludes .github/, _site/, _sass/, _includes/, .git/ and
    other non-content directories.
    """
    excluded_roots = {".github", "_site", ".git", "node_modules",
                      "__pycache__", ".jekyll-cache", ".bundle"}
    dirs: set[str] = set()
    for dirpath, dirnames, _ in os.walk(repo_root):
        rel = os.path.relpath(dirpath, repo_root)
        if rel == ".":
            dirnames[:] = [d for d in dirnames if d not in excluded_roots]
            continue
        top = rel.split(os.sep)[0]
        if top in excluded_roots:
            dirnames.clear()
            continue
        dirs.add(rel.replace(os.sep, "/"))
    return dirs


def collect_files(base_dir: str, suffix: str) -> list[str]:
    """Collect all files under *base_dir* ending with *suffix*.

    Returns paths relative to *base_dir*.
    """
    results: list[str] = []
    if not os.path.isdir(base_dir):
        return results
    for dirpath, _, filenames in os.walk(base_dir):
        for fname in filenames:
            if fname.endswith(suffix):
                rel = os.path.relpath(os.path.join(dirpath, fname), base_dir)
                results.append(rel)
    return results


def collect_all_files(base_dir: str) -> list[str]:
    """Collect ALL files under *base_dir*.

    Returns paths relative to *base_dir*.
    """
    results: list[str] = []
    if not os.path.isdir(base_dir):
        return results
    for dirpath, _, filenames in os.walk(base_dir):
        for fname in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fname), base_dir)
            results.append(rel)
    return results


def collect_subdirs(base_dir: str) -> set[str]:
    """Collect all subdirectory paths (relative) under *base_dir*."""
    dirs: set[str] = set()
    if not os.path.isdir(base_dir):
        return dirs
    for dirpath, dirnames, _ in os.walk(base_dir):
        for d in dirnames:
            full = os.path.join(dirpath, d)
            rel = os.path.relpath(full, base_dir)
            dirs.add(rel.replace(os.sep, "/"))
    return dirs


# Segment pattern: lowercase letters, digits, hyphens.
# Allow "README" as a conventional exception everywhere.
_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _is_kebab_case(dot_stem: str) -> bool:
    """Check that every dot-separated segment is kebab-case (or README)."""
    for seg in dot_stem.split("."):
        if seg == "README":
            continue
        if not _KEBAB_RE.match(seg):
            return False
    return True


def _effective_dir_stem(rel_dir: str, suffix_keyword: str) -> str:
    """Compute dir stem, omitting segments matching the suffix keyword.

    Per the deduplication rule: if a path component matches the suffix keyword
    (e.g. 'template' for .template.* files), omit it from the dot-prefix so
    the keyword appears only once (in the suffix).

    Per the leading-dot rule: a path segment whose name begins with a dot
    (e.g. '.github') is encoded without that leading dot, since the dot is the
    dot-prefix segment separator ('.github/prompts' -> 'github.prompts').
    """
    if not rel_dir or rel_dir == ".":
        return ""
    parts = rel_dir.replace(os.sep, "/").strip("/").split("/")
    filtered = [
        (p[1:] if p.startswith(".") else p)
        for p in parts
        if p != suffix_keyword
    ]
    return ".".join(filtered)


def _check_stem_depth(errors: list, display_path: str, stem: str,
                      dir_stem: str, rel_dir: str, type_base: str,
                      type_name: str, project_dirs: set[str],
                      error_mismatch: str,
                      last_segment_is_action: bool = False) -> None:
    """Strict check: stem must encode exactly the directory path.

    Allowed forms (instructions / templates):
        stem == dir_stem                  (bare)
        stem == dir_stem + '.descriptor'  (one extra segment)

    Allowed forms when *last_segment_is_action* (prompts):
        stem == dir_stem + '.action'      (one extra = action, OK)
        stem == dir_stem + '.path.action' (middle segments are path → check)

    If an extra segment matches an existing subdirectory (in .github/{type}/
    or in the project tree), it should be a path segment — flag with
    'stem-deeper-than-dir'.

    If there are two or more *path* segments after the directory prefix, the
    stem encodes a deeper path than the file's location — always flag.
    """
    if not dir_stem:
        return  # nothing to check for root-level files

    if stem == dir_stem:
        return  # bare — exact match

    dir_path = rel_dir.replace(os.sep, "/")

    if stem.startswith(dir_stem + "."):
        extra = stem[len(dir_stem) + 1:]
        extra_parts = extra.split(".")

        # For prompts, the last segment is always the action — only check
        # the segments BETWEEN the dir prefix and the action.
        if last_segment_is_action:
            path_parts = extra_parts[:-1]  # strip action
            if not path_parts:
                return  # single segment = just the action — OK
        else:
            path_parts = extra_parts

        if len(path_parts) == 1:
            # Single descriptor/path segment — check if it matches a subdir
            candidate = dir_path + "/" + path_parts[0]
            gh_exists = os.path.isdir(os.path.join(type_base, candidate))
            proj_exists = candidate in project_dirs
            if gh_exists or proj_exists:
                loc = ".github/" + type_name if gh_exists else "project"
                errors.append((
                    display_path,
                    "stem-deeper-than-dir",
                    f"Stem '{stem}' encodes subdir '{path_parts[0]}' beyond "
                    f"its directory (exists in {loc}) — move file to "
                    f".github/{type_name}/{candidate}/"
                ))
        else:
            # Multiple path segments — stem encodes a deeper path
            # Find the deepest matching subdir for the error message
            deepest = None
            for i in range(len(path_parts), 0, -1):
                candidate = dir_path + "/" + "/".join(path_parts[:i])
                gh_exists = os.path.isdir(os.path.join(type_base, candidate))
                proj_exists = candidate in project_dirs
                if gh_exists or proj_exists:
                    deepest = candidate
                    break
            if deepest:
                errors.append((
                    display_path,
                    "stem-deeper-than-dir",
                    f"Stem '{stem}' encodes path beyond its directory — "
                    f"subdir '{deepest}' exists; move file to "
                    f".github/{type_name}/{deepest}/"
                ))
            else:
                errors.append((
                    display_path,
                    "stem-deeper-than-dir",
                    f"Stem '{stem}' has {len(path_parts)} path segments "
                    f"('{'.'.join(path_parts)}') after directory prefix "
                    f"'{dir_stem}' — at most 1 descriptor segment expected"
                ))
    else:
        errors.append((
            display_path,
            error_mismatch,
            f"Stem '{stem}' doesn't match directory path '{dir_path}' "
            f"(expected '{dir_stem}' or '{dir_stem}.{{descriptor}}')"
        ))


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def check_instructions(repo_root: str, delta_files: set[str] | None = None,
                       project_dirs: set[str] | None = None) -> list[tuple[str, str, str]]:
    """Validate instruction files. Returns list of (file, error_type, detail).

    If *delta_files* is given, only files whose repo-relative path is in the
    set are checked (delta mode).
    """
    if project_dirs is None:
        project_dirs = set()
    errors: list[tuple[str, str, str]] = []
    base = os.path.join(repo_root, ".github", "instructions")

    for rel_path in collect_files(base, ".instructions.md"):
        rel_norm = rel_path.replace(os.sep, "/")
        if delta_files is not None and f".github/instructions/{rel_norm}" not in delta_files:
            continue
        full_path = os.path.join(base, rel_path)
        fname = os.path.basename(rel_path)
        rel_dir = os.path.dirname(rel_path)

        # Check: suffix keyword appears only once (at the end)
        if fname.count(".instructions.") > 1:
            errors.append((
                f".github/instructions/{rel_norm}",
                "duplicate-suffix",
                f"'.instructions.' appears {fname.count('.instructions.')} "
                f"times in '{fname}' — must appear only once (as the suffix)"
            ))

        # Check: applyTo frontmatter
        fm = parse_frontmatter(full_path)
        if "applyTo" not in fm:
            errors.append((
                f".github/instructions/{rel_norm}",
                "instruction-missing-applyto",
                "Missing 'applyTo' in YAML front matter"
            ))

        # Check: kebab-case (allow README as conventional exception)
        stem = fname.removesuffix(".instructions.md")
        if not _is_kebab_case(stem):
            errors.append((
                f".github/instructions/{rel_norm}",
                "not-kebab-case",
                f"Stem '{stem}' is not lowercase kebab-case with dots"
            ))

        # Check: no consecutive duplicate segments (e.g. diagram.diagram)
        segs = stem.split(".")
        for i in range(len(segs) - 1):
            if segs[i] == segs[i + 1]:
                errors.append((
                    f".github/instructions/{rel_norm}",
                    "consecutive-duplicate-segment",
                    f"Stem '{stem}' has consecutive duplicate segment "
                    f"'{segs[i]}' at positions {i} and {i + 1}"
                ))
                break  # report first occurrence only

        # Check: stem must encode exactly the directory path
        # Rule: {dir-path-as-dots}[.{descriptor}].instructions.md
        # Skip known exceptions (root-level globals, etc.)
        if rel_path.replace(os.sep, "/") in {
            k.replace(os.sep, "/") for k in KNOWN_INSTRUCTION_EXCEPTIONS
        }:
            continue

        eff_stem = _effective_dir_stem(rel_dir, "instructions")
        _check_stem_depth(
            errors,
            f".github/instructions/{rel_norm}",
            stem, eff_stem, rel_dir, base,
            "instructions", project_dirs,
            "instruction-filename-mismatch",
        )

    # Check for non-instruction files in instructions/
    for rel_path in collect_all_files(base):
        rel_norm = rel_path.replace(os.sep, "/")
        if delta_files is not None and f".github/instructions/{rel_norm}" not in delta_files:
            continue
        fname = os.path.basename(rel_path)
        if fname.endswith(".instructions.md"):
            continue
        # Allow non-.md helper files (scripts, data, etc.)
        if not fname.endswith(".md"):
            continue
        errors.append((
            f".github/instructions/{rel_norm}",
            "wrong-suffix",
            f"Markdown file in instructions/ should end with "
            f"'.instructions.md', got '{fname}'"
        ))

    return errors


def check_prompts_retired(repo_root: str) -> list[tuple[str, str, str]]:
    """Fail on any reintroduced prompt artifact under .github/.

    Flags every file under `.github/prompts/` and every `*.prompt.*` file
    anywhere under `.github/` (templates included).

    Deliberately ignores *delta_files*: the ban is a property of the tree, not
    of the changed set, so it is enforced identically on delta and full scans.
    """
    errors: list[tuple[str, str, str]] = []
    github_dir = os.path.join(repo_root, ".github")
    if not os.path.isdir(github_dir):
        return errors

    for dirpath, _dirnames, filenames in os.walk(github_dir):
        rel_dir = os.path.relpath(dirpath, repo_root).replace(os.sep, "/")
        in_prompts_dir = (
            rel_dir == ".github/prompts" or rel_dir.startswith(".github/prompts/")
        )
        for fname in sorted(filenames):
            if not in_prompts_dir and ".prompt." not in fname:
                continue
            errors.append((
                f"{rel_dir}/{fname}",
                "prompt-file-retired",
                PROMPT_RETIRED_DETAIL,
            ))

    return errors


def check_templates(repo_root: str, delta_files: set[str] | None = None,
                    project_dirs: set[str] | None = None) -> list[tuple[str, str, str]]:
    """Validate template files. Returns list of (file, error_type, detail).

    If *delta_files* is given, only files whose repo-relative path is in the
    set are checked (delta mode).
    """
    if project_dirs is None:
        project_dirs = set()
    errors: list[tuple[str, str, str]] = []
    base = os.path.join(repo_root, ".github", "templates")

    # Collect template files (any extension: .template.md, .template.eml, etc.)
    template_pattern = re.compile(r"\.template\.\w+$")

    for rel_path in collect_all_files(base):
        rel_norm = rel_path.replace(os.sep, "/")
        if delta_files is not None and f".github/templates/{rel_norm}" not in delta_files:
            continue
        fname = os.path.basename(rel_path)
        rel_dir = os.path.dirname(rel_path)

        if not template_pattern.search(fname):
            # Non-template file in templates/ — flag it
            errors.append((
                f".github/templates/{rel_norm}",
                "wrong-suffix",
                f"File in templates/ should match '*.template.{{ext}}' "
                f"pattern, got '{fname}'"
            ))
            continue

        # Check: suffix keyword appears only once
        template_count = fname.count(".template.")
        if template_count > 1:
            errors.append((
                f".github/templates/{rel_norm}",
                "duplicate-suffix",
                f"'.template.' appears {template_count} "
                f"times in '{fname}' — must appear only once (as the suffix)"
            ))

        # Extract the prefix (stem before .template.{ext})
        m = re.match(r"^(.+)\.template\.\w+$", fname)
        if not m:
            continue
        prefix = m.group(1)

        # Check: kebab-case (allow README as conventional exception)
        if not _is_kebab_case(prefix):
            errors.append((
                f".github/templates/{rel_norm}",
                "not-kebab-case",
                f"Prefix '{prefix}' is not lowercase kebab-case with dots"
            ))

        # Check: no consecutive duplicate segments (e.g. diagram.diagram)
        segs = prefix.split(".")
        for i in range(len(segs) - 1):
            if segs[i] == segs[i + 1]:
                errors.append((
                    f".github/templates/{rel_norm}",
                    "consecutive-duplicate-segment",
                    f"Prefix '{prefix}' has consecutive duplicate segment "
                    f"'{segs[i]}' at positions {i} and {i + 1}"
                ))
                break  # report first occurrence only

        # Check: stem should not contain "template" as a dot-segment
        # (deduplication rule — if dir path contains template/, omit it
        # from the dot-prefix so the keyword appears only in the suffix)
        prefix_segments = prefix.split(".")
        if "template" in prefix_segments:
            errors.append((
                f".github/templates/{rel_norm}",
                "stem-contains-suffix-keyword",
                f"Prefix '{prefix}' contains 'template' as a segment — "
                f"omit the 'template/' dir from the dot-prefix "
                f"(the suffix '.template.*' already provides the keyword)"
            ))

        # Check: prefix must encode exactly the directory path
        # Pattern: {dir-path-as-dots}[.{descriptor}].template.{ext}
        # For dirs containing 'template/', effective stem omits that segment.
        if not rel_dir:
            continue

        eff_stem = _effective_dir_stem(rel_dir, "template")
        _check_stem_depth(
            errors,
            f".github/templates/{rel_norm}",
            prefix, eff_stem, rel_dir, base,
            "templates", project_dirs,
            "template-filename-mismatch",
        )

    return errors


def _subdir_exists_with_wildcard(subdir: str, project_dirs: set[str]) -> bool:
    """Check if *subdir* matches a project path, allowing wildcard intermediates.

    Templates and instructions may represent patterns like
    toolkit/agenda/participant-pool/ which maps to
    toolkit/agenda/*/participant-pool/ in the actual project.
    """
    parts = subdir.split("/")

    # Try replacing each segment with a wildcard (match any project dir segment)
    for i in range(len(parts)):
        for proj in project_dirs:
            proj_parts = proj.split("/")
            if len(proj_parts) < len(parts):
                continue
            # Try matching: allow project to have extra segments between
            # the .github subdir parts (wildcard intermediates)
            if _match_parts_flexible(parts, proj_parts):
                return True

    return False


def _match_parts_flexible(pattern_parts: list[str], target_parts: list[str]) -> bool:
    """Check if pattern_parts can match target_parts with at most one wildcard gap."""
    # Direct match at same depth
    if len(pattern_parts) == len(target_parts):
        return all(p == t for p, t in zip(pattern_parts, target_parts))

    # Allow one wildcard gap: pattern a/b/c matches target a/b/X/c
    if len(target_parts) == len(pattern_parts) + 1:
        # Try inserting a wildcard at each position
        for skip in range(1, len(target_parts)):
            before_match = all(
                p == t for p, t in zip(pattern_parts[:skip], target_parts[:skip])
            )
            after_match = all(
                p == t for p, t in
                zip(pattern_parts[skip:], target_parts[skip + 1:])
            )
            if before_match and after_match:
                return True

    return False


def check_mirror_structure(repo_root: str, project_dirs: set[str] | None = None) -> list[tuple[str, str, str]]:
    """Check that subdirs under .github/{type}/ mirror real project folders."""
    errors: list[tuple[str, str, str]] = []
    if project_dirs is None:
        project_dirs = get_project_dirs(repo_root)

    for mirror_type in MIRROR_TYPES:
        base = os.path.join(repo_root, ".github", mirror_type)
        if not os.path.isdir(base):
            continue

        subdirs = collect_subdirs(base)
        for subdir in sorted(subdirs):
            # Skip known organisational dirs
            if subdir in {k.replace(os.sep, "/") for k in KNOWN_ORGANISATIONAL_DIRS}:
                continue

            # Check if this matches a real project directory
            if subdir in project_dirs:
                continue

            parts = subdir.split("/")

            # Authoring-guide mirror: .github/instructions/github/<folder>
            # mirrors the customization folders themselves. Per the leading-dot
            # rule the literal .github project folder is encoded without its
            # leading dot, so 'github' here maps to the real '.github' dir on
            # disk (which is an excluded root, hence absent from project_dirs).
            # Scoped to the instructions tree only — the authoring guides live
            # exclusively under .github/instructions/, so allowing a 'github/'
            # subtree under .github/prompts/ or .github/templates/ would wrongly
            # bypass the orphan-mirror check for those trees.
            if (
                mirror_type == "instructions"
                and parts[0] == "github"
                and (
                    os.path.isdir(os.path.join(repo_root, ".github", *parts[1:]))
                    or (len(parts) == 2 and parts[1] in MIRROR_TYPES)
                )
            ):
                continue

            # template/ folders are content-template groupings, not project mirrors
            if parts[-1] == "template":
                continue

            # lifecycle-events/ folders are standard sub-structure
            if parts[-1] == "lifecycle-events":
                parent = "/".join(parts[:-1])
                if parent in project_dirs:
                    continue

            # foundation/ subfolders under domains mirror domain/foundation/**
            if "foundation" in parts:
                foundation_idx = parts.index("foundation")
                parent_path = "/".join(parts[:foundation_idx + 1])
                if parent_path in project_dirs:
                    continue

            # Check with wildcard intermediate matching
            # (e.g. toolkit/agenda/participant-pool -> toolkit/agenda/*/participant-pool)
            if _subdir_exists_with_wildcard(subdir, project_dirs):
                continue

            errors.append((
                f".github/{mirror_type}/{subdir}",
                "mirror-orphan-subdir",
                f"Directory has no matching project folder at '{subdir}'"
            ))

    return errors


def check_misplaced_files(repo_root: str, delta_files: set[str] | None = None) -> list[tuple[str, str, str]]:
    """Ensure .instructions.md, .prompt.md, and .template.* live only in .github/.

    The copilot-instructions state: 'Never create .template.md files in project
    folders. Templates and instructions live exclusively in .github/.'
    """
    errors: list[tuple[str, str, str]] = []
    excluded_roots = {".github", "sources", "_site", ".git", "node_modules",
                      "__pycache__", ".jekyll-cache", ".bundle"}
    template_re = re.compile(r"\.template\.\w+$")

    for dirpath, dirnames, filenames in os.walk(repo_root):
        rel_dir = os.path.relpath(dirpath, repo_root)
        if rel_dir == ".":
            dirnames[:] = [d for d in dirnames if d not in excluded_roots]
        else:
            top = rel_dir.split(os.sep)[0]
            if top in excluded_roots:
                dirnames.clear()
                continue

        for fname in filenames:
            rel_file = os.path.relpath(
                os.path.join(dirpath, fname), repo_root
            ).replace(os.sep, "/")

            if delta_files is not None and rel_file not in delta_files:
                continue

            if fname.endswith(".instructions.md"):
                errors.append((
                    rel_file,
                    "misplaced-file",
                    f"Instruction file found outside .github/ — "
                    f"move to .github/instructions/"
                ))
            elif fname.endswith(".prompt.md"):
                errors.append((
                    rel_file,
                    "prompt-file-retired",
                    PROMPT_RETIRED_DETAIL,
                ))
            elif template_re.search(fname):
                errors.append((
                    rel_file,
                    "misplaced-file",
                    f"Template file found outside .github/ — "
                    f"move to .github/templates/"
                ))

    return errors


def check_agents(repo_root: str, delta_files: set[str] | None = None) -> list[tuple[str, str, str]]:
    """Validate agent definition files in .github/agents/.

    Convention: {name}.agent.md with 'name' and 'description' frontmatter.
    """
    errors: list[tuple[str, str, str]] = []
    base = os.path.join(repo_root, ".github", "agents")

    for rel_path in collect_all_files(base):
        rel_norm = rel_path.replace(os.sep, "/")
        if delta_files is not None and f".github/agents/{rel_norm}" not in delta_files:
            continue
        fname = os.path.basename(rel_path)
        full_path = os.path.join(base, rel_path)

        if not fname.endswith(".agent.md"):
            errors.append((
                f".github/agents/{rel_norm}",
                "wrong-suffix",
                f"File in agents/ should match '*.agent.md' pattern, got '{fname}'"
            ))
            continue

        stem = fname.removesuffix(".agent.md")
        if not _is_kebab_case(stem):
            errors.append((
                f".github/agents/{rel_norm}",
                "not-kebab-case",
                f"Agent name '{stem}' is not lowercase kebab-case"
            ))

        fm = parse_frontmatter(full_path)
        if "name" not in fm:
            errors.append((
                f".github/agents/{rel_norm}",
                "agent-missing-name",
                "Missing 'name' in YAML front matter"
            ))
        elif fm["name"].strip().strip('"').strip("'") != stem:
            errors.append((
                f".github/agents/{rel_norm}",
                "agent-name-mismatch",
                f"'name: {fm['name']}' must equal the filename stem '{stem}' "
                f"(dotted folder path the agent operates on, e.g. 'toolkit.dev.cr')"
            ))
        if "description" not in fm:
            errors.append((
                f".github/agents/{rel_norm}",
                "agent-missing-description",
                "Missing 'description' in YAML front matter"
            ))
        if "model" in fm:
            errors.append((
                f".github/agents/{rel_norm}",
                "agent-has-model",
                "Agent files must not set a 'model' key — the model is chosen "
                "by the person running the agent"
            ))

    return errors


def check_skills(repo_root: str, delta_files: set[str] | None = None) -> list[tuple[str, str, str]]:
    """Validate skill packages in .github/skills/.

    Convention: each skill is a subfolder with a SKILL.md file containing
    'name' and 'description' frontmatter.
    """
    errors: list[tuple[str, str, str]] = []
    base = os.path.join(repo_root, ".github", "skills")
    if not os.path.isdir(base):
        return errors

    for entry in os.listdir(base):
        skill_dir = os.path.join(base, entry)
        if not os.path.isdir(skill_dir):
            continue

        skill_file = os.path.join(skill_dir, "SKILL.md")
        rel_skill = f".github/skills/{entry}/SKILL.md"

        if not os.path.isfile(skill_file):
            if delta_files is not None and rel_skill not in delta_files:
                continue
            errors.append((
                f".github/skills/{entry}",
                "skill-missing-file",
                f"Skill folder '{entry}' is missing SKILL.md"
            ))
            continue

        if delta_files is not None and rel_skill not in delta_files:
            continue

        fm = parse_frontmatter(skill_file)
        if "name" not in fm:
            errors.append((
                rel_skill,
                "skill-missing-name",
                "Missing 'name' in YAML front matter"
            ))
        if "description" not in fm:
            errors.append((
                rel_skill,
                "skill-missing-description",
                "Missing 'description' in YAML front matter"
            ))

    for rel_path in collect_all_files(base):
        rel_norm = rel_path.replace(os.sep, "/")
        if delta_files is not None and f".github/skills/{rel_norm}" not in delta_files:
            continue
        fname = os.path.basename(rel_path)
        if fname == "SKILL.md":
            continue
        errors.append((
            f".github/skills/{rel_norm}",
            "wrong-suffix",
            f"File in skills/ should be 'SKILL.md', got '{fname}'"
        ))

    return errors


def check_leading_fence(repo_root: str, delta_files: set[str] | None = None) -> list[tuple[str, str, str]]:
    """Flag customization .md files that begin with a code-fence wrapper.

    A wrapped file (e.g. opens with ```prompt and closes with ``` at EOF) hides
    its YAML frontmatter, so the file never activates. It must start directly
    with the '---' frontmatter block.

    Enforced on both delta and full scans. When ``delta_files`` is supplied the
    check is limited to those changed files; a full scan (``delta_files is
    None``) inspects every customization file. There is no legacy debt to
    grandfather — every fence-wrapped file has been unwrapped — so the
    push-to-main full scan guards against any wrapper reappearing.
    """
    errors: list[tuple[str, str, str]] = []
    for mirror_type in ("instructions", "agents", "skills"):
        base = os.path.join(repo_root, ".github", mirror_type)
        if not os.path.isdir(base):
            continue
        for rel_path in collect_all_files(base):
            if not rel_path.endswith(".md"):
                continue
            rel_norm = rel_path.replace(os.sep, "/")
            rel_repo = f".github/{mirror_type}/{rel_norm}"
            if delta_files is not None and rel_repo not in delta_files:
                continue
            fence = starts_with_fence(os.path.join(base, rel_path))
            if fence:
                errors.append((
                    rel_repo,
                    "leading-fence-wrapper",
                    f"File starts with a code fence ('{fence}') — a "
                    f"customization file must begin with its '---' YAML "
                    f"frontmatter, not a fenced-code wrapper. Remove the "
                    f"opening fence and its matching closing fence."
                ))
    return errors


_ALLOWED_SCRIPT_EXTENSIONS = frozenset({
    ".py", ".ps1", ".sh", ".yml", ".yaml", ".json", ".gql", ".md",
})


def check_scripts(repo_root: str, delta_files: set[str] | None = None) -> list[tuple[str, str, str]]:
    """Validate top-level script filenames in .github/scripts/.

    Only files directly under .github/scripts/ (non-recursive) are validated.
    Subdirectories such as .github/scripts/github/ and .github/scripts/toolkit/
    hold bundled per-topic assets that follow their own naming conventions and
    are intentionally excluded here.

    Top-level files (except README.md) must have a lowercase kebab-case stem and
    one of the allowed extensions: .py, .ps1, .sh, .yml, .yaml, .json, .gql, .md.
    """
    errors: list[tuple[str, str, str]] = []
    base = os.path.join(repo_root, ".github", "scripts")
    if not os.path.isdir(base):
        return errors

    for entry in os.listdir(base):
        full = os.path.join(base, entry)
        if not os.path.isfile(full):
            continue
        if delta_files is not None and f".github/scripts/{entry}" not in delta_files:
            continue
        if entry == "README.md":
            continue
        stem, ext = os.path.splitext(entry)
        if not _KEBAB_RE.match(stem):
            errors.append((
                f".github/scripts/{entry}",
                "not-kebab-case",
                f"Script filename '{entry}' is not lowercase kebab-case"
            ))
        if ext.lower() not in _ALLOWED_SCRIPT_EXTENSIONS:
            allowed = ", ".join(sorted(_ALLOWED_SCRIPT_EXTENSIONS))
            errors.append((
                f".github/scripts/{entry}",
                "disallowed-extension",
                f"Script extension '{ext}' is not allowed (allowed: {allowed})"
            ))

    return errors


def check_hooks(repo_root: str, delta_files: set[str] | None = None,
                project_dirs: set[str] | None = None) -> list[tuple[str, str, str]]:
    """Validate hook definition files in .github/hooks/.

    Hook filenames mirror the project folder of the thing they support, but the
    file itself lives flat in .github/hooks/ so it loads from the default
    registered location. A hook that backs a demo under workspace/demo/ is named
    with that path as a dot-prefix (e.g. workspace.demo.hooks-tour.json) and
    sits directly in .github/hooks/.

    Convention:
      - lives flat in .github/hooks/ (a mirrored subfolder is allowed but must
        be registered separately in chat.hookFilesLocations)
      - filename is a lowercase kebab-case dot-prefix matching the mirrored
        project path, optionally plus one descriptor segment, with a .json
        extension
      - the JSON parses and carries a top-level 'hooks' object whose keys are
        recognised event names
    """
    if project_dirs is None:
        project_dirs = set()
    errors: list[tuple[str, str, str]] = []
    base = os.path.join(repo_root, ".github", "hooks")
    if not os.path.isdir(base):
        return errors

    for rel_path in collect_all_files(base):
        rel_norm = rel_path.replace(os.sep, "/")
        if delta_files is not None and f".github/hooks/{rel_norm}" not in delta_files:
            continue
        fname = os.path.basename(rel_path)
        rel_dir = os.path.dirname(rel_path)
        full_path = os.path.join(base, rel_path)

        if fname == "README.md":
            continue

        if not fname.endswith(".json"):
            errors.append((
                f".github/hooks/{rel_norm}",
                "wrong-suffix",
                f"File in hooks/ should be a '*.json' hook definition, "
                f"got '{fname}'"
            ))
            continue

        stem = fname.removesuffix(".json")

        if not _is_kebab_case(stem):
            errors.append((
                f".github/hooks/{rel_norm}",
                "not-kebab-case",
                f"Stem '{stem}' is not lowercase kebab-case with dots"
            ))

        segs = stem.split(".")
        for i in range(len(segs) - 1):
            if segs[i] == segs[i + 1]:
                errors.append((
                    f".github/hooks/{rel_norm}",
                    "consecutive-duplicate-segment",
                    f"Stem '{stem}' has consecutive duplicate segment "
                    f"'{segs[i]}' at positions {i} and {i + 1}"
                ))
                break

        if rel_dir:
            eff_stem = _effective_dir_stem(rel_dir, "hooks")
            _check_stem_depth(
                errors,
                f".github/hooks/{rel_norm}",
                stem, eff_stem, rel_dir, base,
                "hooks", project_dirs,
                "hook-filename-mismatch",
            )
        elif len(segs) >= 2:
            mirrored_dir = "/".join(segs[:-1])
            mirrored_matches = (
                mirrored_dir in project_dirs
                or _subdir_exists_with_wildcard(mirrored_dir, project_dirs)
            )

            # Leading-dot rule: 'github' in the hook stem maps to '.github'.
            if not mirrored_matches:
                parts = mirrored_dir.split("/")
                mirrored_matches = (
                    parts[0] == "github"
                    and os.path.isdir(os.path.join(repo_root, ".github", *parts[1:]))
                )

            if not mirrored_matches:
                errors.append((
                    f".github/hooks/{rel_norm}",
                    "hook-filename-mismatch",
                    f"Flat hook stem '{stem}' should encode an existing mirrored "
                    f"project path in all but the last segment; "
                    f"'{mirrored_dir}' does not match any project directory"
                ))

        try:
            with open(full_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            errors.append((
                f".github/hooks/{rel_norm}",
                "hook-invalid-json",
                f"Hook file is not valid JSON: {exc}"
            ))
            continue

        hooks_obj = data.get("hooks") if isinstance(data, dict) else None
        if not isinstance(hooks_obj, dict):
            errors.append((
                f".github/hooks/{rel_norm}",
                "hook-missing-hooks-key",
                "Missing top-level 'hooks' object mapping event names to "
                "command arrays"
            ))
            continue

        for event_name in hooks_obj:
            if event_name not in _HOOK_EVENTS:
                allowed = ", ".join(sorted(_HOOK_EVENTS))
                errors.append((
                    f".github/hooks/{rel_norm}",
                    "hook-unknown-event",
                    f"Unknown hook event '{event_name}' "
                    f"(allowed: {allowed})"
                ))

    return errors


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
        if arg == "--stdin":
            continue
        repo_root = os.path.abspath(arg)
        break

    # Delta mode: read changed file list from stdin
    delta_files: set[str] | None = None
    if use_stdin:
        raw = sys.stdin.read()
        delta_files = {
            line.strip().replace(os.sep, "/")
            for line in raw.splitlines()
            if line.strip()
        }
        if not delta_files:
            print("\nNo files to check (empty delta). ✅")
            sys.exit(0)

    project_dirs = get_project_dirs(repo_root)

    all_errors: list[tuple[str, str, str]] = []
    all_errors.extend(check_instructions(repo_root, delta_files, project_dirs))
    all_errors.extend(check_prompts_retired(repo_root))
    all_errors.extend(check_templates(repo_root, delta_files, project_dirs))
    all_errors.extend(check_agents(repo_root, delta_files))
    all_errors.extend(check_skills(repo_root, delta_files))
    all_errors.extend(check_scripts(repo_root, delta_files))
    all_errors.extend(check_hooks(repo_root, delta_files, project_dirs))
    all_errors.extend(check_leading_fence(repo_root, delta_files))
    all_errors.extend(check_mirror_structure(repo_root, project_dirs))
    all_errors.extend(check_misplaced_files(repo_root, delta_files))

    # Count files checked for the summary
    if delta_files is not None:
        files_checked = len(delta_files)
    else:
        files_checked = 0
        for mirror_type in (*MIRROR_TYPES, "agents", "skills", "scripts"):
            base = os.path.join(repo_root, ".github", mirror_type)
            if os.path.isdir(base):
                files_checked += len(collect_all_files(base))

    scan_label = f"delta — {len(delta_files)} file(s)" if delta_files else "full"

    is_ci = os.environ.get("CI") == "true"

    # ---- GitHub Actions annotations (CI only) ----
    if is_ci:
        for filepath, error_type, detail in all_errors:
            print(f"::error file={filepath},line=1::[{error_type}] {detail}")

    # ---- Console summary (always) ----
    print()

    if all_errors:
        by_type: dict[str, int] = {}
        for _, t, _ in all_errors:
            by_type[t] = by_type.get(t, 0) + 1

        print(f"Scanned {files_checked} file(s) ({scan_label} scan), "
              f"found {len(all_errors)} issue(s):")
        for t, c in sorted(by_type.items()):
            print(f"  {t}: {c}")

        # Group errors by file for readable output
        from collections import defaultdict
        by_file: dict[str, list] = defaultdict(list)
        for filepath, error_type, detail in all_errors:
            by_file[filepath].append((error_type, detail))

        print()
        for filepath, issues in sorted(by_file.items()):
            print(f"  {filepath}")
            for error_type, detail in issues:
                print(f"    Line 1: [{error_type}] {detail}")
            print()

        # ---- GitHub Actions Job Summary ----
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## 📂 .github/ Structure Issues\n\n")
                sf.write(f"Scanned **{files_checked}** file(s) ({scan_label} scan), "
                         f"found **{len(all_errors)}** issue(s).\n\n")
                sf.write("| Type | File | Line | Detail |\n")
                sf.write("|------|------|-----:|--------|\n")
                for filepath, error_type, detail in all_errors:
                    safe_detail = detail.replace("|", "\\|")
                    sf.write(
                        f"| `{error_type}` "
                        f"| `{filepath}` "
                        f"| 1 "
                        f"| {safe_detail} |\n"
                    )

        sys.exit(1)
    else:
        print(f"Scanned {files_checked} file(s) ({scan_label} scan) — "
              f"all .github/ structure checks passed. ✅")

        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## 📂 .github/ Structure\n\n")
                sf.write(f"Scanned **{files_checked}** file(s) ({scan_label} scan) — "
                         f"all structure checks passed. ✅\n")

        sys.exit(0)


if __name__ == "__main__":
    main()
