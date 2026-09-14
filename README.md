# ijk-compilers
Validated interpreters of the ijk language created by Judah De Paula.

## What's here

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
