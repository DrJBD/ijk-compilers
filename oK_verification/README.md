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

- **The harness has to know every error message oK can print.** It
  first matched only "... error." and "has not been defined.", so a
  parse error, an unexpected character, "noun expected" and "function
  or list expected" all came back as passes. The patterns now cover
  every message `oK.js` throws, anchored to the start of a line, with
  a real trigger for each in `test_run_ok_test.py`.
- **oK mis-reads `\\` before `n`, `t` or `"`** in a string literal --
  see `stage2_j_to_k/README.md`.
- **Non-ASCII displays truncated but is stored whole.** oK prints an em
  dash as the byte `0x14`, but `0+"—"` is `8212`. Strings are UTF-16
  code units (an emoji is two). Check content by code, not by printed
  form.

## The "ok" -> "oK" normalization rule

Judah's own instruction, 2026-09-14: the ijk compiler should treat
lowercase "ok" as a valid transform into the properly-cased "oK" --
i.e., a casual reference to the interpreter by its ordinary-English
name normalizes to its real one. Implemented in stage 2 as a `.k`
validator (`stage2_j_to_k/validators.py`), the same way "(...)" ->
"---" is stage 1's rule.

## Using it directly

`assert_k_ok(...)` checks any `.k` source against the real
interpreter -- hand-written, stage 2 output, or anything else -- and
works on its own, without the rest of the pipeline. `pipeline.py` at
the repo root uses it for the last two stages of an end-to-end run.
