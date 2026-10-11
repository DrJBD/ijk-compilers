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
  `.j` file's content as a K dict: `text` (the file, exactly) plus
  `title`/`body` as a view; `validators.py`
  checks already-produced `.k` source (currently the `ok` -> `oK`
  rule). `fixtures/` holds a synthetic sample file for the round-trip
  test. See that directory's own README.
- **`oK_verification/`** -- the test harness. `run_ok_test.py` runs K
  source through the real `oK` interpreter and reports errors; K's
  REPL exits 0 even on failure, so it reads the output instead. See
  that directory's own README.

## Running the whole pipeline

`pipeline.py` runs `.i` (or `.j`) files through every stage in order
and reports how far each got: readiness, compile, validate, evaluate
in oK, then a round-trip check that the `.k` holds the source
exactly, computed separately inside oK and in Python.

```sh
python3 pipeline.py path/to/file.i path/to/dir/
python3 pipeline.py path/to/dir/ --out build/   # also write .j and .k
```

It writes nothing unless given `--out`, and never renames or edits a
source file.

`ijk_files.py` makes and takes apart `.ij` (a `.i` and `.j` merged)
and `.ijk` (all three in one file), and `check` tests a `.ijk` as a
Rosetta stone: does the `k` say exactly what the `j` says, and where
does the `j` differ from the `i`. See `samples/README.md` for what
each file type is, with
sample `.k` output that runs on its own in oK.

## Feeding oK

`feed.py` turns any mix of `.i`, `.j`, `.k` and `.ijk` files into one
self-contained K program. It defines `docs` (each document's `.k`
dict) and `corpus` (the same documents as columns: `name`, `title`,
`body`, `text`). The `.i` side never goes in: `.i` and `.ij` files are
refused, a `.ijk` contributes only its `k` or `j`, and a folder's `.i`
files are skipped.

```sh
python3 feed.py samples/ -o feed.k        # then: node ~/code/ok/repl.js feed.k
python3 feed.py samples/ -e 'corpus`title'
python3 feed.py samples/ --prelude candidate_ops.k -e 'find["oK"]'
```

The output also pastes into oK's browser REPL. Which operations belong
on top of the corpus is open; `candidate_ops.k` holds tested
candidates and `OPERATIONS.md` the open questions.

## Viewing a context

`viewer/build_viewer.py` takes the same arguments as `feed.py` and
writes one HTML file with oK and the feed inside it. Open it in a
browser, with no network needed: the documents are listed by name and
title, clicking one shows its exact text, and a box runs K against the
loaded context.

```sh
python3 viewer/build_viewer.py samples/ --prelude candidate_ops.k -o viewer.html
```

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
python3 test_pipeline.py
python3 test_ijk_files.py
python3 test_feed.py
python3 viewer/test_viewer.py
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
