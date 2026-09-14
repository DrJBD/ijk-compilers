# stage2_j_to_k

`.j` -> `.k`, the second half of the ijk pipeline (stage 1,
`.i` -> `.j`, lives in `stage1_i_to_j/`).

## Deliberately minimal -- what this is and isn't

The real open question from when this stage was first discussed --
what it actually means to "compile" prose into K, versus a
NOTATION_PROPOSAL.md-style arithmetic expression -- is **not
answered here**. What this does: represent a `.j` file's content as
real K *data* (a dict, `title`/`body`), verified valid against the
actual `oK` interpreter (`~/code/ok`). It does not claim the result
is "executable" in any deeper sense than "a K program that holds this
document's content and parses cleanly." Extending what compilation
means beyond that is a real design decision for later, not assumed
here.

## Files

- **`transform.py`** -- `j_to_k(path)` / `compile_j_to_k(j, k)`. String
  escaping (`\"`, `\n`, `\\`) and dict-literal syntax confirmed
  directly against oK before writing this, not assumed.
- **`validators.py`** -- checks that run against already-produced `.k`
  source, separate from generation, per Judah's own architectural
  call: "The ok->oK rule is defined as one of the .k file validators."
  Currently one rule: lowercase "ok" outside a string literal should
  be "oK". Scoped deliberately to *code* (comments, bare identifiers),
  not to string content -- rewriting words inside a user's actual
  quoted prose would be a materially different, more sensitive act
  than normalizing a code-level tool reference, and isn't assumed
  wanted here.
- **`test_transform.py`** / **`test_validators.py`** -- 5 + 8 tests,
  all verified against the real interpreter or exercising real edge
  cases (escaped quotes inside strings, word-boundary false positives
  on "book"/"token", already-correct input left alone).

## Real edge case the tests caught

A `\"` inside a K string literal doesn't close the string -- the
validator's boundary tracker has to skip the escaped character
entirely, not just the backslash, or it misreads where the string
actually ends. Covered by
`test_escaped_quote_inside_string_does_not_break_boundary_tracking`.
