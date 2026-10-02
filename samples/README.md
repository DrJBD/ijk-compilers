# i, j and k files

ijk is the pipeline that takes a piece of writing from a collaborative draft,
to an author's confirmed words, to data in K.

| File | What it is | How a file gets there |
|---|---|---|
| `.i` | A collaborative draft. Others, an AI included, may have written parts of it, and it may still hold open questions. | Written by anyone. |
| `.j` | The author's confirmed words, with nothing left open. It starts as an exact copy of the `.i`, and the author may revise it from there. | Promoted from a `.i` with no blocking markers. Stage 1 only reports whether a file is ready; the author does the promoting. |
| `.k` | The `.j` as K data, which runs in [oK](https://github.com/JohnEarnest/ok). | Compiled from a `.j` by stage 2. |
| `.ij` | The merged result of a `.i` and a `.j`. | `ijk_files.py merge`. |
| `.ijk` | The `.i`, `.j` and `.k` together in one file. | `ijk_files.py pack`. |

Both combined formats are lossless: `split` and `unpack` give back the
original files byte for byte, line endings included.

## Writing a `.i`

The first line is the title and everything after it is the body. A marker
counts only at the start of a line.

| Marker | Meaning | Blocks promotion? |
|---|---|---|
| `-` | Approved | no |
| `--` | Draft paragraph, not reviewed yet | no |
| `-?` | Inline question, either party can ask | no |
| `---` followed by text | "I want your recommendation" | **yes** |
| `?` on its own | An AI couldn't confirm that a `-?` was answered | **yes** |
| `(...)`, anywhere on a line | Unfinished; same as `---` | **yes** |

## The `.k` a file compiles to

It's a dict with three keys:

- `` `text `` holds the file exactly, down to the line endings.
- `` `title `` is the first line, trimmed.
- `` `body `` is the rest, trimmed.

## The `.ij` and `.ijk` formats

**`.ij`.** Lines the `.i` and `.j` share appear once. Where they
differ, both versions appear in a git-style block, so any editor that
highlights merge conflicts highlights these:

```
<<<<<<< .i
-? Should the last line stay?
=======
The author's own rewrite of that paragraph.
>>>>>>> .j
```

A promoted `.j` is identical to its `.i`, so their `.ij` is just the
text. A source line that is exactly one of the marker lines is refused
rather than mangled.

**`.ijk`.** Each file sits under a banner in the house `.i` style. The
byte count in the banner, not a search for `====`, is what marks where
the section ends, so a file can contain `====` lines of its own:

```
============================================================
i: hello.i (170 bytes)
============================================================
Hello, oK
...
```

## Samples

Sources are in `src/`. Every output here comes from
`python3 samples/build.py`; a test fails if they drift. Each finished
sample has a `.j`, `.k`, `.ij` and `.ijk`.

- **`hello`** (`.i` → `.j` → `.k`). Uses all three non-blocking markers.
- **`escapes`** (`.i` → `.j` → `.k`). Has CRLF line endings, literal `\n`
  and `\r\n` written as text, quotes, a tab, an em dash and an emoji.
  Carriage returns and backslashes are written as `` `c$13 `` and
  `` `c$92 `` (see `stage2_j_to_k/README.md` for why).
- **`revised`**. The author rewrote the `.j` after promotion (`src/`
  has both), so `revised.ij` shows the drafted paragraph and its
  question beside the rewrite.
- **`open`** (`.i` only). Stops at the readiness check because of a
  `---` question, so it never becomes anything else:

  ```
  FAIL  open.i -- stopped at readiness
        line 3: [---] --- Which of the two readings should the body take?
  ```

Each `.k` runs on its own in oK, the same way oK's own `examples/` do:

```sh
node ~/code/ok/repl.js samples/hello.k
# [title:"Hello, oK";body:"- An approved line: ...";text:"Hello, oK\n- An ..."]
```

oK prints a string that contains non-ASCII as hex (the em dash shows as
the byte `14`), but it stores the whole character: `0+"—"` is `8212`. To
read the samples in the interactive REPL, paste one in as `d:` followed by
the dict, then:

```
d[`title]
#d[`text]           / length, in UTF-16 code units
0+d[`text]          / the exact character codes
```
