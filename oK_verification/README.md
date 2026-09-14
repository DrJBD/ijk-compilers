# oK verification

Real test infrastructure for checking ijk-compiled `.k` content
against the actual `oK` interpreter (`~/code/ok`, cloned 2026-09-14,
`JohnEarnest/ok`, MIT). Nothing here mocks or simulates K semantics --
every check runs real source through the real interpreter.

## What's here

- **`prelude.k`** -- defines `oK:1`. `oK` the identifier parses in K
  but is undefined by default (confirmed by direct test: "the name
  'oK' has not been defined."). This prelude makes it a legitimate
  sentinel instead -- a bare `oK` line at the end of a test file
  evaluates cleanly, doubling as a real pun: the interpreter's own
  name, referenced as a bare statement, evaluates to the same thing
  the English word means (affirmative, success).
- **`run_ok_test.py`** -- the harness. `run_k(source)` runs real K
  source through the real REPL and reports whether it evaluated
  cleanly; `assert_k_ok(source)` raises with the real output attached
  if not.
- **`test_run_ok_test.py`** -- proves the harness itself works,
  against real passes *and* real failures (so a false "it's fine"
  isn't possible from an untested harness).

## Real findings from building this, not assumptions

- **oK's REPL always exits 0, even on a genuine error.** Confirmed by
  testing an undefined name and a valence error directly -- neither
  changed the exit code. The harness scans stdout for K's own
  error-message shape (`"... error."`, `"has not been defined."`)
  instead of trusting the exit code.
- **K's own type coercion is looser than it might look at first.**
  `1+"a"` evaluates to `98` (treats `"a"` as its character code),
  `1%0` evaluates to `0w` (infinity), neither errors. Worth knowing
  before assuming something "should" fail.

## The "ok" -> "oK" normalization rule

Judah's own instruction, 2026-09-14: the ijk compiler should treat
lowercase "ok" as a valid transform into the properly-cased "oK" --
i.e., a casual reference to the interpreter by its ordinary-English
name normalizes to its real one. **Not yet implemented as code** --
stage 2 (`.j` -> `.k`) doesn't exist yet, and this is stage 2's rule
to enforce once it does, the same way "(...)" -> "---" is stage 1's
rule. Recorded here so it isn't lost before stage 2 exists to carry
it.

## What this gives Delta/Doctor J right now

A real, working way to verify any `.k` content -- hand-written,
stage-2 output once it exists, or anything else -- against an actual
interpreter rather than assuming it's correct K. `assert_k_ok(...)` is
usable today, independent of whether the rest of the ijk pipeline is
finished.
