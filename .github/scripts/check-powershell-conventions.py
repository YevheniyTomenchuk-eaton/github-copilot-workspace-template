#!/usr/bin/env python3
"""Enforce the PowerShell helper conventions.

Four rules from .github/copilot-instructions.md are checked for the agent-run
helper scripts under .github/scripts/ and the customization files that call
them:

  Rule A  (script side)  — "Guard required parameters at the script side with a
          `$(throw)` default." A top-level `param()` block in an agent-run
          script must NOT declare a Mandatory attribute in any form — both the
          explicit `[Parameter(Mandatory = $true)]` and the bare shorthand
          `[Parameter(Mandatory)]` are banned (only `Mandatory = $false` is
          allowed). A missing mandatory parameter drops PowerShell into an
          interactive `Supply values for the following parameters:` prompt that
          HANGS the agent forever. The script-side fix is a throwing default —
          `[string]$Owner = $(throw 'Required parameter -Owner was not provided.')`
          — which fails fast in any host. This rule bans the Mandatory attribute
          so the throwing default is used instead.

  Rule B  (call site)    — "Always launch `.ps1` helpers with
          `-NoProfile -NonInteractive`." Every invocation must pass
          `-NoProfile`; a non-interactive helper must additionally pass
          `-NonInteractive`. Conversely a script that *deliberately* prompts
          the user (Read-Host / Get-Credential) must NOT be
          launched with `-NonInteractive`, or the prompt throws instead of
          appearing — but it must still carry `-NoProfile`.

  Rule C  (script encoding) — "Agent-run .ps1 helpers must be pure ASCII."
          These scripts are launched through `powershell.exe` (Windows
          PowerShell 5.1), which reads a BOM-less source file using the
          machine's ANSI code page — NOT UTF-8. A literal non-ASCII character
          (em-dash, ellipsis, arrow, accented letter, …) is then decoded from
          its raw UTF-8 bytes into the wrong glyphs; when those bytes happen to
          land on a structural character (quote, brace, paren) the whole file
          fails to tokenize and the helper dies with a syntax error that never
          reproduces on a UTF-8 host. This rule bans every literal character
          above U+007F in a script under .github/scripts/. Emit runtime
          non-ASCII with an escape instead — `[char]0x2014` for an em-dash,
          `[char]::ConvertFromUtf32(0x1F512)` for an emoji — exactly as
          pull-state.ps1 already does.

    Rule D  (native Git capture) — Never directly capture `git ... 2>&1`.
                    Windows PowerShell 5.1 can surface normal Git stderr progress as
                    NativeCommandError records even when Git exits zero. Use the shared
                    `invoke-git-command.ps1` helper and inspect its ExitCode and Output.

Auto-skip (Rule A) — a script is exempt from the Mandatory ban only when the
attribute is genuinely required and cannot hang the agent:
  - it uses `ParameterSetName` (conditional mandatoriness — a param is only
    mandatory within one set), OR
  - it carries the explicit opt-out marker `# ps-conventions:allow-mandatory`
    anywhere in the file.

Interactivity (Read-Host / Get-Credential / UI prompts / web-login) no longer
exempts Rule A. A required parameter still gets a throwing default so an omitted value
fails fast, while the script's own body prompts collect user input unchanged —
the throwing default only fires when the parameter is absent, never when the
script runs normally. The interactive signal governs Rule B only (the call site
must omit -NonInteractive so those body prompts can appear).

Only the *top-level* param block is inspected. `Mandatory` inside a nested
`function` of a dot-sourced library never causes the hang (those functions are
called in-process with real arguments) and is ignored.

Usage:
  python check-powershell-conventions.py [REPO_ROOT]          # full scan
  echo "file1\\nfile2" | python check-powershell-conventions.py --stdin

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

SCRIPTS_DIR = os.path.join(".github", "scripts")

# Customization files whose PowerShell invocations are checked for Rule B.
CALLSITE_DIRS = (
    os.path.join(".github", "prompts"),
    os.path.join(".github", "instructions"),
    os.path.join(".github", "agents"),
    os.path.join(".github", "skills"),
    os.path.join(".github", "hooks"),
    SCRIPTS_DIR,
)
CALLSITE_EXTS = (".md", ".json", ".ps1")

# Signals that a script legitimately prompts the user (console prompt, domain
# credential dialog, or browser sign-in). The prompt is intended behaviour, so
# the call-site must NOT force -NonInteractive.
INTERACTIVE_SIGNAL = re.compile(
    r"(?im)(?:"
    r"Read-Host|Get-Credential|\$Host\.UI\.(?:Prompt|ReadLine)|"
    r"Connect-PnPOnline|Connect-MgGraph|Connect-AzAccount|Connect-ExchangeOnline|"
    r"-UseWebLogin"
    r")"
)

# Explicit marker for a script that is interactive by transitivity (it calls
# another interactive script) or by a mechanism the signal above cannot see.
# Honoured by both rules exactly like the interactive signal.
INTERACTIVE_MARKER = re.compile(r"(?i)#\s*ps-conventions:interactive")

# Conditional mandatoriness — a param is mandatory only inside one set. Banning
# it here would be wrong, so the whole script is exempt from Rule A.
PARAMSET_SIGNAL = re.compile(r"(?i)ParameterSetName")

# Explicit per-script opt-out for the rare intentional Mandatory.
ALLOW_MARKER = re.compile(r"(?i)#\s*ps-conventions:allow-mandatory")

# A Mandatory attribute in any of its forms — the explicit `Mandatory = $true`
# and the bare shorthand `[Parameter(Mandatory)]` both make a param mandatory
# (and can hang the agent). Only `Mandatory = $false` is harmless, so it is
# excluded via negative lookahead. The optional `= $true` is consumed so the
# parameter-name search below starts past it, not on the `$true` literal.
MANDATORY = re.compile(r"(?i)\bMandatory\b(?:\s*=\s*\$true)?(?!\s*=\s*\$false)")

# A PowerShell invocation that launches a .ps1 through -File. Captures the
# script path so its interactivity can be resolved.
INVOKE = re.compile(
    r"(?i)\b(?:powershell(?:\.exe)?|pwsh)\b[^\n]*?-File\s+"
    r"['\"]?([^'\"\s]+\.ps1)['\"]?"
)

FLAG_NOPROFILE = re.compile(r"(?i)-NoProfile\b")
FLAG_NONINTERACTIVE = re.compile(r"(?i)-NonInteractive\b")

# Any character outside the 7-bit ASCII range. A literal occurrence in an
# agent-run .ps1 helper corrupts tokenization under Windows PowerShell 5.1
# (Rule C); it must be emitted with a [char]0xNNNN escape instead.
NON_ASCII = re.compile(r"[^\x00-\x7F]")

GIT_STDERR_CAPTURE = re.compile(
    r"(?i)(?:^|[\s(=;|])(?:&\s*)?(?:git(?:\.exe)?|\$gitCommand)\b[^\r\n]*2>&1"
)
GIT_CAPTURE_HELPER = os.path.join(
    ".github", "scripts", "github", "invoke-git-command.ps1"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(full):
    try:
        with open(full, "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _is_interactive(text):
    return bool(INTERACTIVE_SIGNAL.search(text) or INTERACTIVE_MARKER.search(text))


def _in_scripts(rel):
    rel = rel.replace("/", os.sep)
    return rel == SCRIPTS_DIR or rel.startswith(SCRIPTS_DIR + os.sep)


def _in_callsite_scope(rel):
    rel = rel.replace("/", os.sep)
    if not rel.lower().endswith(CALLSITE_EXTS):
        return False
    return any(rel == d or rel.startswith(d + os.sep) for d in CALLSITE_DIRS)


def find_tracked(repo_root, pattern):
    """Yield relative paths of tracked files matching a git ls-files pattern."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", pattern],
            cwd=repo_root, capture_output=True, text=True, check=True,
        )
        return [p.replace("/", os.sep) for p in result.stdout.split("\0") if p]
    except (FileNotFoundError, subprocess.CalledProcessError):
        out = []
        for dirpath, _dirs, files in os.walk(repo_root):
            for fname in files:
                rel = os.path.relpath(os.path.join(dirpath, fname), repo_root)
                out.append(rel)
        return out


def _top_level_param_block(text):
    """Return (start_line, block_text) for the top-level param() block.

    The top-level block is the first `param(` that appears before any
    `function` keyword. A `param(` that only appears after a function
    definition belongs to that function (a dot-sourced library) and is not a
    hang risk, so None is returned.
    """
    lines = text.split("\n")
    first_function = None
    for idx, line in enumerate(lines):
        if re.match(r"(?i)^\s*function\s+[\w-]+", line):
            first_function = idx
            break

    param_line = None
    for idx, line in enumerate(lines):
        if re.match(r"(?i)^\s*param\s*\(", line):
            param_line = idx
            break

    if param_line is None:
        return None
    if first_function is not None and first_function < param_line:
        return None

    depth = 0
    started = False
    collected = []
    for idx in range(param_line, len(lines)):
        line = lines[idx]
        collected.append(line)
        for ch in line:
            if ch == "(":
                depth += 1
                started = True
            elif ch == ")":
                depth -= 1
        if started and depth <= 0:
            break
    return param_line, "\n".join(collected)


def _param_name_after(block, pos):
    """Name the parameter whose declaration follows a Mandatory match."""
    m = re.search(r"\$(\w+)", block[pos:])
    return m.group(1) if m else "?"


def _resolve_script(repo_root, raw_path):
    """Resolve a captured .ps1 invocation path to a repo-relative file, or None."""
    norm = raw_path.replace("\\", "/")
    marker = ".github/scripts/"
    i = norm.lower().find(marker)
    if i != -1:
        rel = norm[i:].replace("/", os.sep)
    else:
        rel = norm.replace("/", os.sep)
    full = os.path.join(repo_root, rel)
    return rel if os.path.isfile(full) else None


# ---------------------------------------------------------------------------
# Rule A — script side
# ---------------------------------------------------------------------------

def check_script(rel_path, repo_root):
    full = os.path.join(repo_root, rel_path)
    text = _read(full)
    if text is None:
        return []

    if PARAMSET_SIGNAL.search(text) or ALLOW_MARKER.search(text):
        return []

    block = _top_level_param_block(text)
    if block is None:
        return []

    start_line, block_text = block
    line_offset = start_line
    violations = []
    for m in MANDATORY.finditer(block_text):
        name = _param_name_after(block_text, m.end())
        line_no = line_offset + block_text[:m.start()].count("\n") + 1
        violations.append((
            line_no,
            "mandatory-param",
            f"Parameter -{name} declares a Mandatory attribute "
            f"([Parameter(Mandatory = $true)] or the [Parameter(Mandatory)] "
            f"shorthand) - an "
            f"omitted value makes the agent hang on an interactive prompt. "
            f"Replace it with a throwing default: "
            f"[type]${name} = $(throw 'Required parameter -{name} was not "
            f"provided.'). The throwing default fires only when the "
            f"argument is omitted, so a script that prompts the user "
            f"(Read-Host / Get-Credential) still collects input from its "
            f"body unchanged. For a rare intentional Mandatory, carry the "
            f"'# ps-conventions:allow-mandatory' opt-out marker.",
        ))
    return violations


# ---------------------------------------------------------------------------# Rule C - script encoding (ASCII-only)
# ---------------------------------------------------------------------------

def check_ascii(rel_path, repo_root):
    full = os.path.join(repo_root, rel_path)
    text = _read(full)
    if text is None:
        return []

    violations = []
    for line_no, line in enumerate(text.split("\n"), start=1):
        m = NON_ASCII.search(line)
        if m is None:
            continue
        ch = m.group(0)
        violations.append((
            line_no,
            "non-ascii-char",
            f"Line contains a literal non-ASCII character '{ch}' (U+{ord(ch):04X}) "
            f"at column {m.start() + 1}. Windows PowerShell 5.1 reads this "
            f"BOM-less script with the machine's ANSI code page, so the "
            f"character's raw UTF-8 bytes are mis-decoded and can break "
            f"tokenization. Replace it with an escape emitted at runtime - "
            f"e.g. [char]0x{ord(ch):04X} - as pull-state.ps1 does.",
        ))
    return violations


# ---------------------------------------------------------------------------
# Rule D - Windows PowerShell-safe native Git capture
# ---------------------------------------------------------------------------

def check_git_capture(rel_path, repo_root):
    if rel_path.replace("/", os.sep) == GIT_CAPTURE_HELPER:
        return []

    full = os.path.join(repo_root, rel_path)
    text = _read(full)
    if text is None:
        return []

    lines = text.split("\n")
    violations = []
    for index, line in enumerate(lines):
        if GIT_STDERR_CAPTURE.search(line) is None:
            continue

        violations.append((
            index + 1,
            "unsafe-git-stderr-capture",
            "Direct `git ... 2>&1` capture can throw NativeCommandError under "
            "Windows PowerShell 5.1 even when Git exits zero. Only the "
            "canonical capture helper may redirect Git stderr. Dot-source "
            ".github/scripts/github/invoke-git-command.ps1 and use "
            "Invoke-GitCommand, then inspect its ExitCode and Output fields.",
        ))
    return violations


# ---------------------------------------------------------------------------# Rule B — call site
# ---------------------------------------------------------------------------

def check_callsite(rel_path, repo_root, interactive_cache):
    full = os.path.join(repo_root, rel_path)
    text = _read(full)
    if text is None:
        return []

    violations = []
    for line_no, line in enumerate(text.split("\n"), start=1):
        for m in INVOKE.finditer(line):
            target = _resolve_script(repo_root, m.group(1))
            if target is None:
                continue
            if target not in interactive_cache:
                tt = _read(os.path.join(repo_root, target))
                interactive_cache[target] = bool(tt and _is_interactive(tt))
            is_interactive = interactive_cache[target]
            has_noprofile = bool(FLAG_NOPROFILE.search(line))
            has_noninteractive = bool(FLAG_NONINTERACTIVE.search(line))
            disp = target.replace(os.sep, "/")

            if is_interactive:
                if not has_noprofile:
                    violations.append((
                        line_no,
                        "missing-noprofile",
                        f"Invocation of {disp} is missing -NoProfile. Every "
                        f"helper invocation must pass -NoProfile (it keeps the "
                        f"child shell clean and fast); only -NonInteractive is "
                        f"conditional on the target being non-interactive.",
                    ))
                if has_noninteractive:
                    violations.append((
                        line_no,
                        "interactive-noninteractive",
                        f"Invocation of interactive script {disp} passes "
                        f"-NonInteractive - the script prompts the user "
                        f"(Read-Host / Get-Credential), so -NonInteractive "
                        f"makes the prompt throw. Remove the flag.",
                    ))
            else:
                missing = []
                if not has_noprofile:
                    missing.append("-NoProfile")
                if not has_noninteractive:
                    missing.append("-NonInteractive")
                if missing:
                    violations.append((
                        line_no,
                        "missing-launch-flags",
                        f"Invocation of {disp} is missing "
                        f"{' and '.join(missing)}. Non-interactive helpers must "
                        f"launch with -NoProfile -NonInteractive so a wrong "
                        f"call fails fast instead of hanging.",
                    ))
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
        raw = [f.strip().replace("/", os.sep)
               for f in sys.stdin.read().splitlines() if f.strip()]
        script_files = [f for f in raw if f.lower().endswith(".ps1") and _in_scripts(f)]
        callsite_files = [f for f in raw if _in_callsite_scope(f)]
    else:
        script_files = [f for f in find_tracked(repo_root, "*.ps1") if _in_scripts(f)]
        callsite_files = [f for f in find_tracked(repo_root, ".github")
                          if _in_callsite_scope(f)]

    all_violations = []
    files_checked = 0
    interactive_cache = {}

    for rel in script_files:
        if not os.path.isfile(os.path.join(repo_root, rel)):
            continue
        files_checked += 1
        for line_no, vtype, detail in check_script(rel, repo_root):
            all_violations.append((rel, line_no, vtype, detail))
        for line_no, vtype, detail in check_ascii(rel, repo_root):
            all_violations.append((rel, line_no, vtype, detail))
        for line_no, vtype, detail in check_git_capture(rel, repo_root):
            all_violations.append((rel, line_no, vtype, detail))

    for rel in callsite_files:
        if not os.path.isfile(os.path.join(repo_root, rel)):
            continue
        files_checked += 1
        for line_no, vtype, detail in check_callsite(rel, repo_root, interactive_cache):
            all_violations.append((rel, line_no, vtype, detail))

    is_ci = os.environ.get("CI") == "true"
    if is_ci:
        for rel, line_no, vtype, detail in all_violations:
            gh_path = rel.replace(os.sep, "/")
            print(f"::error file={gh_path},line={line_no}::[{vtype}] {detail}")

    print()
    print(f"Scanned {files_checked} file(s).")

    if all_violations:
        by_type = defaultdict(int)
        for _, _, t, _ in all_violations:
            by_type[t] += 1

        print(f"Found {len(all_violations)} PowerShell-convention violation(s):")
        for t, c in sorted(by_type.items()):
            print(f"  {t}: {c}")

        by_file = defaultdict(list)
        for rel, line_no, vtype, detail in all_violations:
            by_file[rel.replace(os.sep, "/")].append((line_no, vtype, detail))

        print()
        for filepath, issues in sorted(by_file.items()):
            print(f"  {filepath}")
            for line_no, vtype, detail in sorted(issues):
                print(f"    Line {line_no}: [{vtype}] {detail}")
            print()

        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as sf:
                sf.write("## ⚠️ PowerShell Convention Violations\n\n")
                sf.write(
                    f"Scanned **{files_checked}** files, found "
                    f"**{len(all_violations)}** violation(s) in "
                    f"**{len(by_file)}** file(s).\n\n"
                )
                sf.write("| Type | File | Line | Detail |\n")
                sf.write("|------|------|-----:|--------|\n")
                for rel, line_no, vtype, detail in all_violations:
                    gh_path = rel.replace(os.sep, "/")
                    safe = detail.replace("|", "\\|")
                    sf.write(f"| `{vtype}` | `{gh_path}` | {line_no} | {safe} |\n")

        sys.exit(1)

    print("No PowerShell-convention violations found. ✅")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as sf:
            sf.write("## ✅ PowerShell Convention Check\n\n")
            sf.write(
                f"Scanned **{files_checked}** files — no violations. ✅\n"
            )


if __name__ == "__main__":
    main()
