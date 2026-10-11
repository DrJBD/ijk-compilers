# ijk-compilers
Validated interpreters of the ijk language created by Judah De Paula.

An AI can draft anything; only a person can confirm it, and the tools
enforce the difference.

## How you'd use it

If you've used tracked changes in a word processor, you already know the
pattern. There's the document with everyone's suggestions still in it,
the clean copy once you've accepted the ones you want, and the PDF you
actually send. ijk gives each of those its own file, as plain text:

| File | Like | Who writes it |
|---|---|---|
| `.i` | the document with suggestions on | anyone: you, a colleague, an AI |
| `.j` | the clean copy you accepted | only you |
| `.k` | the PDF you send | the compiler, from the `.j`, checked |

The difference from tracked changes is that tools check the rules, so
they don't depend on habit alone. The pipeline won't pass a `.i` that
still has an open question. Nothing from a `.i` goes into a feed for
another program or AI. And the `.k` can be checked at any time against
the `.j` it came from.

**A working session looks like this:**

1. Start a `.i`. The first line is the title. Write what you have.
2. Bring in the AI to work in the same file. Its lines go in as drafts
   (`--`) or questions (`-?`). Yours can too.
3. Read it through. Mark the lines you accept with `-`. That marker means
   approved, so only you should write it. Rewrite or delete the rest.
   Anything that needs a real decision before you go on gets `---`.
4. Run `python3 pipeline.py yourfile.i`. It lists anything still open.
   Repeat 2–4 until it passes.
5. Save the passing file as `yourfile.j`. That's your confirmed text.
   From here on, only you edit it.
6. When a website, a script or another AI needs the text, compile the
   `.j` to a `.k`. `ijk_files.py check` proves later that it still says
   what you confirmed.

One short file, start to finish:

```
dinner.i (in progress)                      dinner.j (confirmed)
-----------------------------------------   ------------------------------
Dinner Friday                               Dinner Friday
- Friday at 7, at our place.                Friday at 7, at our place.
-- Bring a dessert if you like.             Bring a dessert if you like.
--- Is the Smiths' allergy nuts or dairy?   Nothing with nuts, please.
```

The AI drafted the dessert line (`--`) and you kept it. The `---` line
stops the `.i` from passing until someone finds out. Once you've written
the answer in, it passes, and you save it as the `.j`. The `.j` is your
clean copy, so the markers can go.

**When it's worth it:** anything an AI helped write that goes out under
your name; anything someone has to sign off; anything where you may later
need to show exactly what was approved, and that it reached its readers
unchanged. For a quick note to a friend, it isn't.

New here? [`EXAMPLES.md`](EXAMPLES.md) walks through what ijk is for,
step by step, on three small examples you can run.

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
python3 pipeline.py path/to/dir/ --out build/   # also write the output
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

Then, from the repo root:

```sh
python3 run_tests.py
```

It runs every test file and prints one line each, and the full output of
any file that fails. `test_examples.py` among them runs every command in
`EXAMPLES.md` and checks its output. There's no test framework: each
file also runs on its own, from its own directory.

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
