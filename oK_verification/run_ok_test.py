"""
Real test harness for verifying ijk-compiled .k content against the
actual oK interpreter (~/code/ok/repl.js) -- not a mock, not a
simulation of K semantics. Every check here runs real K source
through the real interpreter and inspects its real output.

Confirmed by direct testing, 2026-09-14, not assumed:
- oK's REPL always exits 0, even on a genuine error ("valence error.",
  "the name 'x' has not been defined."). Exit code alone cannot detect
  failure -- this harness scans stdout for oK's own error-message
  shape instead ("... error." / "has not been defined.").
- `oK` (the identifier) parses but is undefined by default. This
  harness prepends prelude.k (oK:1) to every run so a bare `oK` line
  at the end of a test file is a legitimate, evaluable success marker.
"""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).parent
_PRELUDE = _HERE / "prelude.k"
_REPL = Path.home() / "code" / "ok" / "repl.js"

# K error messages observed directly: "valence error.", "the name 'x'
# has not been defined.", "type error." (per oK's docs/Manual.md
# error list) -- matched by the shared "<...> error." shape, plus the
# specific "has not been defined" phrasing since it doesn't end that
# way.
_ERROR_PATTERNS = [
    re.compile(r"\berror\.\s*$", re.MULTILINE),
    re.compile(r"has not been defined\."),
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
            f"oK REPL not found at {_REPL} -- clone JohnEarnest/ok first."
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
