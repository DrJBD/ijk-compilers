"""
Real test harness for verifying ijk-compiled .k content against the
actual oK interpreter (repl.js from JohnEarnest/ok, found via the
OK_REPL environment variable, default ~/code/ok/repl.js) -- not a
mock, not a simulation of K semantics. Every check here runs real K
source through the real interpreter and inspects its real output.

Confirmed by direct testing, 2026-09-14, not assumed:
- oK's REPL always exits 0, even on a genuine error ("valence error.",
  "the name 'x' has not been defined."). Exit code alone cannot detect
  failure -- this harness scans stdout for oK's own error-message
  shape instead ("... error." / "has not been defined.").
- `oK` (the identifier) parses but is undefined by default. This
  harness prepends prelude.k (oK:1) to every run so a bare `oK` line
  at the end of a test file is a legitimate, evaluable success marker.
"""

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).parent
_PRELUDE = _HERE / "prelude.k"
_REPL = Path(
    os.environ.get("OK_REPL", Path.home() / "code" / "ok" / "repl.js")
).expanduser()

# Every error message oK.js can throw, read from its source (each
# `throw new Error(...)`) and triggered for real in
# test_run_ok_test.py. The REPL prints each one on its own output line;
# a value never starts that way (strings print starting with `"`), so
# the patterns are anchored to the start of a line. An earlier version
# matched only "... error." at line end and "has not been defined.",
# which let parse errors, unexpected characters and "... expected"
# messages through as passes.
_ERROR_PATTERNS = [
    re.compile(p, re.MULTILINE)
    for p in (
        r"^\s*\w+ error\..*$",  # length/valence/index/domain/parse error.
        r"^\s*the name '.*' has not been defined\.$",
        r"^\s*unexpected character .*$",
        r"^\s*noun expected following ':'\.$",
        r"^\s*function or list expected, found .*$",
        r"^\s*\w+ expected, found \w+\.$",
        r"^\s*positive int expected\.$",
        r"^\s*malformed byte string\.$",
        r"^\s*invalid arguments to .*$",
    )
]


@dataclass
class OkResult:
    source: str
    stdout: str
    ok: bool
    errors: list  # matched error lines, empty if ok


def run_k(source: str, use_prelude: bool = True) -> OkResult:
    """
    Runs real K source through the real oK REPL and reports whether
    it evaluated cleanly. use_prelude=True (default) prepends
    prelude.k so a bare `oK` reference in `source` is valid.
    """
    if not _REPL.exists():
        raise FileNotFoundError(
            f"oK REPL not found at {_REPL} -- clone JohnEarnest/ok and set "
            "OK_REPL to its repl.js if it isn't at ~/code/ok/repl.js."
        )

    full_source = source
    if use_prelude:
        full_source = _PRELUDE.read_text(encoding="utf-8") + "\n" + source

    proc = subprocess.run(
        ["node", str(_REPL)],
        input=full_source,
        capture_output=True,
        text=True,
        timeout=10,
    )

    errors = []
    for pattern in _ERROR_PATTERNS:
        errors.extend(m.group(0).strip() for m in pattern.finditer(proc.stdout))

    return OkResult(source=source, stdout=proc.stdout, ok=not errors, errors=errors)


def run_k_file(source: str) -> OkResult:
    """
    Runs K source the way `node repl.js FILE` does: parsed as one
    program, only the final value printed, whole (the REPL can spread a
    long value over several lines). An error there is an uncaught
    exception, so a non-zero exit is the failure signal; its message is
    taken from stderr.
    """
    if not _REPL.exists():
        raise FileNotFoundError(f"oK REPL not found at {_REPL}")
    with tempfile.NamedTemporaryFile("w", suffix=".k", delete=False, encoding="utf-8") as f:
        f.write(source)
        path = f.name
    try:
        proc = subprocess.run(
            ["node", str(_REPL), path], capture_output=True, text=True, timeout=30
        )
    finally:
        os.unlink(path)
    errors = []
    if proc.returncode != 0:
        errors = [l.strip() for l in proc.stderr.splitlines() if l.startswith("Error:")] or [
            proc.stderr.strip()
        ]
    return OkResult(source=source, stdout=proc.stdout, ok=not errors, errors=errors)


def assert_k_ok(source: str, use_prelude: bool = True):
    """Raises with the real oK output attached if the source errors."""
    result = run_k(source, use_prelude=use_prelude)
    if not result.ok:
        raise AssertionError(
            f"K source did not evaluate cleanly:\n{source}\n"
            f"--- real oK output ---\n{result.stdout}\n"
            f"--- detected errors ---\n{result.errors}"
        )
    return result
