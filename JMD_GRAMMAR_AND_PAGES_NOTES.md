# `.jmd` Marker Grammar and Pages-Generation Notes

Confirmed through real use, not hypothetical -- worked out live across two
real letters, both taken all the way through to a printed, mailed
document. Examples below are invented/generic, not the real letters
(those stay private, under `~/Documents/Correspondance/` on the author's
own machine, never in this repo -- same boundary `j-notes/spec.yaml`'s
`privacy_boundary` already states for a different layer, applied here to
personal correspondence instead of the `.i` IDENTITY system).

## Relationship to `j-notes/spec.yaml`

`spec.yaml` defines `.jmd`'s *shape* -- the `.j` -> `.jmd` -> `.md`
pipeline stages, and that `--` is "a meta-information marker." It
deliberately stops there: processing/interpretation rules for that
marker were kept out on purpose ("j-notes is a compiler agnostic
language definition... that info should be put into ijk-compilers").
This document is that "info" -- the actual marker semantics, worked out
by running real letters through them and fixing what broke.

## The marker grammar

Five markers, one column of meaning each:

| marker | meaning | blocks `.md` readiness? |
|---|---|---|
| `-` | approved, ready to carry into `.md` | no -- this is the ready state |
| `--` | ordinary draft paragraph, not yet reviewed | no |
| `---` | "I want your recommendation" -- a real open question needing discussion | **yes** |
| `-?` | a question either party (human or AI) can ask the other, inline | no -- a "promise the next layer knows how to interpret it" |
| `?` (bare) | the AI edited/reviewed a `-?` and can't confirm it was truly answered, even though the paragraph itself is otherwise valid | **yes** |

Worked example of the `-?` -> `?` transition: the AI flags something with
`-?` plus a specific question. If a later edit changes the marker back to
plain `--` (or leaves it alone) without the underlying ambiguity actually
being resolved in the text, the AI's next pass should mark it bare `?`,
not silently accept `--` or re-litigate with a fresh `-?`. Bare `?` is
the honest way to say "this looks fine on the surface, but I can't
confirm the real question got answered."

## Syntax: line-scoped, not block-scoped

A marker runs from where it starts to either a second copy of the same
marker later on the *same line* (closing it early -- ordinary content
resumes right after), or to the end of the line if no second marker
appears. Never spans multiple lines on its own -- no `BEGIN`/`END`
pairing the way `.i`'s `CONTEXT` block uses.

```
-- Ordinary example sentence. -- An aside gets closed early here, and this part is plain text again.
```

**Position rule, confirmed: line-initial only.** A marker only triggers
when it's the first thing on a line. The same characters appearing
anywhere else on that line are ordinary text, never marker syntax, no
matter how many appear or how they're punctuated. Settled by checking
real files against the alternative (marker-anywhere): the author's own
established writing habit uses mid-sentence `--` constantly (52 times in
one real file, 21 in another, 7 in a four-line one) -- allowing markers
to trigger mid-line would turn nearly every sentence into a collision
with how the format's own author already writes. Line-initial-only is
the only version of the rule that doesn't fight the author's voice on
every paragraph.

The real cost of this choice, named rather than hidden: a marker can
only ever apply to a whole line/paragraph, never to a sub-span inside
one. Flagging just one clause in the middle of a longer sentence isn't
expressible -- that clause has to be broken onto its own line first.
Every real use case so far has been paragraph-level anyway, so this
reads as the right trade, not a loss.

## Ordering rule

Arranging the `-` (approved) lines into the most logically sensible
reading order is part of doing a pass -- not just flagging content, but
sequencing it. `--` (draft) lines can sit anywhere among the `-` lines
without needing the `-` sequence around them to already be contiguous or
"finished" -- a draft doesn't need to know its final place to exist.

## Pipeline in practice: `.j` -> `.jmd` -> `.md` -> `.pages`

The last hop (finished `.md`-equivalent content into an actual, printable
`.pages` document) isn't part of the `.jmd` spec itself, but it's the
real destination this pipeline was built for, so the findings below are
worth keeping next to the grammar.

## Pages generation via AppleScript -- what actually works

Confirmed by direct testing, not assumed:

**Works:**
- Setting `body text` of a whole document -- fine for a plain,
  unstyled letter with no custom formatting to protect.
- **Setting `paragraph N of body text` individually** -- this is the
  key finding. Per-paragraph replacement preserves surrounding
  paragraphs' formatting (custom fonts, alignment, letterhead styling)
  in a way that whole-document `body text` reassignment does not.
- Extracting `preview.jpg` from inside a `.pages` file (`unzip -l`
  shows it's a real zip/IWA package) for a fast visual sanity check
  without needing to open the GUI at all.

**Does not work -- not exposed via AppleScript, confirmed by testing,
not just undocumented:**
- Paragraph styles (can't read or set a style name).
- Headers/footers as distinct scriptable objects -- querying for a
  `footer` property errors with "variable footer is not defined."
- Margins / page setup -- same error pattern querying `top margin`,
  etc. A `document`'s scriptable properties are limited to `body text`,
  `name`, `file`, `document template`, and a handful of others; nothing
  layout-related.

**Practical recipe that follows from this**, for building or filling a
custom-styled `.pages` template:
1. Duplicate an already-correctly-styled `.pages` file. Never start
   from a whole-document `body text` reassignment if there's styling
   worth protecting.
2. Fill in or clear content paragraph-by-paragraph (`set paragraph N
   of body text to "..."`), never by reassigning the whole `body text`
   property again once it's styled correctly.
3. Printer-margin and header/footer-region issues (e.g., a printer
   clipping content too close to the physical edge) aren't fixable via
   AppleScript at all -- they're a Format sidebar -> Document tab fix
   in Pages itself (checking "Header"/"Footer" and setting a margin
   value). Automating this was tried and confirmed not possible with
   the current scripting dictionary; don't re-attempt without a new
   reason to think it'd work differently.

## Cross-check against real `.i` files

Before trusting this grammar beyond personal letters, checked it against
every real `.i` file available (six total: `compiler.i`,
`RegressionTests.i`, `Syntaxia.song.i`, and three previously-unseen files
in a `Presentations` folder). A follow-up whole-home-directory search
found no others -- these six are the complete set on this machine as of
2026-08-07. No accidental collisions found, but real findings came out
of it:

- **The position rule above came directly from this check** -- one file
  had five mid-sentence `--` in a single line, none of them line-initial;
  safe under line-initial-only, would have shattered under
  marker-anywhere.
- **`-- Context --` (paired, same-line) already works as a header
  convention** with zero new grammar needed -- first `--` opens, second
  closes early, nothing follows. Found in the wild, not designed for.
- **`.i` isn't one shape.** `RegressionTests.i` is Python source code
  wearing a `.i` extension -- its `---` occurrences are all inside `#
  ----` comment dividers, safe by accident (never line-initial), not by
  design. Whether "`.i` must be a valid `.jmd`" is even meant to cover
  `.i` files that are actually executable code, versus only the
  prose/notes-shaped ones, is still an open question -- flagged, not
  answered here.
- **A structural variant exists**: `3DFishbone.i` uses `BEGIN
  IDENTITY`/`END IDENTITY` alongside `BEGIN CONTEXT`/`END CONTEXT`, a
  block type absent from the other files checked.

## `.i` files that are source code

Confirmed, settled: yes, `.i` covers files that are actual machine
source code, not just prose/notes. `RegressionTests.i` (real Python) is
the working example.

**Rule:** when an `.i` file is source code, its `-- Context --` section
goes at the *end* of the file, expressed in whatever comment syntax that
language actually uses -- not bare `--`, since that would break the
file as valid source. For Python specifically, that means every line of
the section prefixed with `#` (Python has no block-comment syntax, so
there's no shortcut around per-line prefixing):

```python
# -- Context --
# whatever context content belongs here, one # per line
```

**Gap closed, 2026-08-07:** `RegressionTests.i` now has one, added at the
end (empty `BEGIN CONTEXT`/`END CONTEXT`, matching the pattern used
elsewhere, wrapped in the header and Python's `#`). Kept deliberately
empty rather than populated by running `parser.py` against the whole
suite -- that classifier is tuned to prose/notes vocabulary, not Python,
and would have dumped most of a multi-thousand-line file into Context as
noise. Verified the file still parses as valid Python after the edit
(`ast.parse`, not a full test run) -- a comment-only addition, so this
was a sanity check, not a real risk.

## Open, not yet done
- No automated tooling exists yet -- every pass described here was done
  by hand, by an AI reading the file and editing it directly. A real
  `.jmd` parser/linter implementing this grammar mechanically is future
  work, not started.
