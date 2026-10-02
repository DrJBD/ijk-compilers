# i, j and k files

ijk is the pipeline that takes a piece of writing from a collaborative draft,
to an author's confirmed words, to data in K.

| File | What it is | How a file gets there |
|---|---|---|
| `.i` | A collaborative draft. Others, an AI included, may have written parts of it, and it may still hold open questions. | Written by anyone. |
| `.j` | The author's confirmed words. The text is the same as the `.i`, with nothing left open. | Promoted from a `.i` with no blocking markers. Stage 1 only reports whether a file is ready; the author does the promoting. |
| `.k` | The `.j` as K data, which runs in [oK](https://github.com/JohnEarnest/ok). | Compiled from a `.j` by stage 2. |

`.ij` and `.ijk` are named in the top-level README but not defined yet.

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

## Samples

Sources are in `src/`. Every output here was produced by
`python3 pipeline.py samples/src --out samples` from the repo root.

- **`hello`** (`.i` → `.j` → `.k`). Uses all three non-blocking markers.
- **`escapes`** (`.i` → `.j` → `.k`). Has CRLF line endings, literal `\n`
  and `\r\n` written as text, quotes, a tab, an em dash and an emoji.
  Carriage returns and backslashes are written as `` `c$13 `` and
  `` `c$92 `` (see `stage2_j_to_k/README.md` for why).
- **`open`** (`.i` only). Stops at the readiness check because of a
  `---` question, so it never becomes a `.j` or a `.k`:

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
