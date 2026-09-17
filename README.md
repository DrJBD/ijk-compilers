# ijk-compilers
Validated interpreters of the ijk language created by Judah De Paula.

## The pipeline

Files move `.i` -> `.j` -> `.k`, and the `.k` output is checked against
a real K interpreter.

- **`stage1_i_to_j/`** -- `.i` -> `.j`. A readiness checker, not a
  rewriter: `transform.py` reports whether a `.i` file still carries
  blocking markers (`markers.py`), and never resolves them or renames
  the file itself.
- **`stage2_j_to_k/`** -- `.j` -> `.k`. `transform.py` represents a
  `.j` file's content as a K dict (`title`/`body`); `validators.py`
  checks already-produced `.k` source (currently the `ok` -> `oK`
  rule). `fixtures/` holds a synthetic sample file for the round-trip
  test. See that directory's own README.
- **`oK_verification/`** -- the test harness. `run_ok_test.py` runs K
  source through the real `oK` interpreter and reports errors; K's
  REPL exits 0 even on failure, so it reads the output instead. See
  that directory's own README.

## Running the tests

Needs Python 3 and Node. Stage 2 and the harness also need a clone of
[JohnEarnest/ok](https://github.com/JohnEarnest/ok):

```sh
git clone https://github.com/JohnEarnest/ok ~/code/ok
```

The harness looks for `~/code/ok/repl.js`. If your clone is somewhere
else, point `OK_REPL` at its `repl.js`:

```sh
export OK_REPL=/path/to/ok/repl.js
```

Each test file runs on its own with no test framework. Run each from
its own directory, starting at the repo root:

```sh
(cd stage1_i_to_j   && python3 test_transform.py)
(cd stage2_j_to_k   && python3 test_transform.py && python3 test_validators.py)
(cd oK_verification && python3 test_run_ok_test.py)
```

## Notes

- **`NOTATION_PROPOSAL.md`** -- moved from `j-notes`, where it was
  drafted under an earlier, since-corrected idea for that repo (a
  human-readable notation compiling directly into K, targeting
  `ktye/i`). That's this repo's job, not `j-notes`'. Still **draft,
  not implemented, not agreed** -- see the file's own status line and
  open questions (§4) before treating anything in it as settled.

- **`JMD_GRAMMAR_AND_PAGES_NOTES.md`** -- the `.jmd` marker grammar
  (`-`/`--`/`---`/`-?`/bare `?`) and how it was actually used to take
  real letters from raw notes to a printed page. Unlike
  `NOTATION_PROPOSAL.md`, this isn't speculative -- it's confirmed by
  real use, including exactly what does and doesn't work when
  generating a `.pages` file via AppleScript.

## Relationship to other repos

- **`j-notes`** depends on this repo, not the other way around --
  `j-notes` converts `.j` raw notes into `.jmd`/`.md`; the `.i`/`.j`/
  `.k`/`.ij`/`.ijk` compiler suite itself lives here.
