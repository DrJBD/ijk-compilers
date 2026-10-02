# What oK can and can't do

Two sources, kept apart. **The repo says** is taken from
`JohnEarnest/ok`'s own `Readme.md` and `docs/Manual.md` (local clone
`~/code/ok`, commit `799c602`, 2026-07-26). **Found here** is what
testing it for this project turned up, with where it's recorded.

## What it is (the repo says)

- A "toy interpreter" for a dialect of K. The Readme says it aims at
  K5; the Manual says k6, "still-evolving", and describes oK's
  *current behavior*.
- "Expect oK to be buggy, incomplete and occasionally flat-out wrong,
  but slowly improving over time."
- Not meant to be fast or "suitable for any practical purpose beyond
  learning"; simplicity of implementation comes first.
- Written in JavaScript. It doesn't distinguish lists from typed
  vectors internally, so adverbs dispatch dynamically on every
  iteration, which the Readme calls "substantial overhead".
- Its own suite (`node test.js`) passes: 749 tests on this clone.

## What it can do (the repo says)

- **Data:** numbers, characters, symbols, lists, dictionaries,
  functions. Strings are lists of characters. Booleans (`101b`) and
  bytes (`0x41`).
- **Verbs:** all 19 K primitives, each with a monadic and a dyadic
  form. These include flip, where, group, find, cast, split and join,
  plus the `$[...]` conditional and the `.[f;x;:]` error trap.
- **Adverbs:** each, eachprior, eachright, eachleft, over, scan and
  their forms (fixedpoint, for, while, window, stencil).
- **Named builtins:** only six. `sin`, `cos`, `exp`, `log`, `prm`
  (permutations), and `in`, which is "left-atomic", so `"y" in s`
  doesn't test for a substring.
- **I/O, command-line REPL** (`node repl.js`):
  - `0:` reads a file as text (a list of lines), or lists a directory.
    `x 0: y` writes text to a file, or to stdout.
  - `1:` reads a file and parses it as JSON into K data.
  - `5:` gives the printable form of a value.
  - `node repl.js FILE` runs a whole file and prints its final value.
- **I/O, browser REPL:** `0:`/`1:` fetch URLs (same-origin rules
  apply). There's an editor pane, and a `?run=` URL runs code.
- **oK Mobile:** plotting (`pl`, `ps`), menus (`6:`), local storage,
  and async HTTP GET and POST (`1:`, `2:`).

## What it says it can't do, or does differently

- No string escapes other than `\n`, `\t`, `\"` and `\\`.
- One character in quotes is a character atom, not a string.
- The command-line REPL is "very simplistic" with no interactive
  debugging. The Readme notes Node's blocking stdin read is
  non-portable; it was tested with Node v0.11.14.
- The parser is ad hoc, "a bit hairy", and "likely to change
  substantially over time".
- Output formatting "may differ in small ways" from other K
  interpreters.

## Found here, not in its docs

| Finding | Where |
|---|---|
| Escapes are undone one kind at a time, so `"\\n"` (backslash, then n) becomes a newline | `stage2_j_to_k/README.md`, Delta Design-70 |
| A raw carriage return in a string breaks the line-based parser | `stage2_j_to_k/README.md` |
| The REPL exits 0 on errors and prints them as ordinary output; file mode crashes Node with a stack trace instead | `run_ok_test.py` |
| Non-ASCII prints as truncated hex bytes but is stored whole, as UTF-16 code units (an emoji is two) | `README.md` here |
| No substring search (`ss` is undefined) | `candidate_ops.k` |
| `list?string` can't find a string in a list of strings | `candidate_ops.k` |
| Take wraps around: `3#"-"` is `"---"` | `candidate_ops.k` |
| `#'` (count each) misparses into a projection; `{#x}'` works | `candidate_ops.k` |
| A list of dicts doesn't become a table, and `+` on a dict doesn't flip it into one | `feed.py` uses column lists instead |
| `` `l$ `` (cast to lowercase) crashes the formatter; `_` lowercases a string | probe, 2026-10-02 |
| `o` is reserved inside a function (it's the function itself, per the Manual), so an argument named `o` silently becomes the function | probe, 2026-10-02 |
| Symbols can't contain `_`: `` `dark_bishop `` splits, and `!` then reads as mod | probe, 2026-10-02 |
