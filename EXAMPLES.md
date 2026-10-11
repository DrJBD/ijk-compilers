# Examples: what ijk is for

More and more writing is done with an AI: it drafts, you edit, and
eventually the result goes out under your name. Three questions get hard
to answer along the way:

- **Is this finished?** Which parts are still drafts, and which questions
  are still open?
- **What did the author actually decide?** Where did the final text move
  away from the draft?
- **Is this still exactly what was approved?** After the text has been
  copied, converted and handed to other programs, does it still say the
  same thing?

ijk answers them with three files for each piece of writing. A **`.i`** is
the shared draft: anyone, an AI included, can write in it, and it can hold
open questions. A **`.j`** holds the author's confirmed words. A **`.k`**
is the `.j` as data for the [K language](https://github.com/JohnEarnest/ok),
so a program can work with it without changing it.

Everything below runs from the repo root on a small example: three
documents for a neighbourhood garden club, in `examples/club/`. Every
command's output on this page is real: `test_examples.py` runs each one
and fails if the page and the tools disagree. Files the examples write go
in `build/`, which git ignores. You need Python 3, Node and a clone of oK
(see `README.md`).

## 1. Is it ready to send?

The club's three drafts, written partly by an AI:

```
examples/club/welcome.i      examples/club/watering.i      examples/club/plot-rules.i
```

`plot-rules.i` still has a question nobody has answered, written with the
`---` marker ("I want your recommendation"), and an unfinished line ending
in `(...)`:

```console
$ cat examples/club/plot-rules.i
Plot Rules
No chemical sprays on shared paths.
--- Should a plot left untended for a month go back to the waiting list, or get a reminder first?
Compost bins are shared. Please turn them weekly.
Dogs are welcome on a leash (...)
```

The pipeline checks every file and refuses to go further with one that
isn't finished:

```console
$ python3 pipeline.py examples/club/
FAIL  plot-rules.i -- stopped at readiness
      plot-rules.i: NOT ready -- 2 blocking marker(s):
        line 3: [---] --- Should a plot left untended for a month go back to the waiting list, or get a reminder first?
        line 5: [(...)] Dogs are welcome on a leash (...)
PASS  watering.i
PASS  welcome.i
PASS  welcome.j

3/4 through to oK
```

Not every marker blocks. In `watering.i`, `--` marks a paragraph nobody
has reviewed yet and `-?` asks a question in passing. Neither stops the
file, because neither means "this needs a decision first":

```console
$ cat examples/club/watering.i
Watering Schedule
Each plot is watered by its own gardener.
-- In the July heat, water before 8 a.m. or after 7 p.m.
-? Is the hose by the shed still leaking?
The rain barrels are for everyone.
```

**Who it helps:** anyone sending out text that went through several
hands. A list of open questions can't quietly go out to the printer.

## 2. Confirm, then compile

Once a `.i` is ready, the author promotes it to a `.j`. The tools never
do that for you; promoting is the author's decision. For `welcome`, the
author rewrote part of the AI's draft and saved the result as
`welcome.j`. For `watering`, the author accepted the draft as it was.

`--out` writes the `.j` and the compiled `.k` for each file that passes:

```console
$ python3 pipeline.py examples/club/watering.i examples/club/welcome.j --out build/corpus/
PASS  watering.i
PASS  welcome.j

2/2 through to oK
```

The `.k` is the text as K data: the title, the body, and the whole file
exactly, line endings included:

```console
$ cat build/corpus/watering.k
`title`body`text!("Watering Schedule";"Each plot is watered by its own gardener.\n-- In the July heat, water before 8 a.m. or after 7 p.m.\n-? Is the hose by the shed still leaking?\nThe rain barrels are for everyone.";"Watering Schedule\nEach plot is watered by its own gardener.\n-- In the July heat, water before 8 a.m. or after 7 p.m.\n-? Is the hose by the shed still leaking?\nThe rain barrels are for everyone.\n")
```

"PASS" means more than "it compiled": the pipeline ran each `.k` in a
real K interpreter and checked, character by character, that it holds
the source.

## 3. What did the author decide?

A `.ij` merges the draft and the final text. Lines they share appear once;
where they differ, both versions appear side by side, in the same format
git uses for merge conflicts, so most editors highlight it:

```console
$ python3 ijk_files.py merge examples/club/welcome.i examples/club/welcome.j -o build/welcome.ij
wrote build/welcome.ij
$ cat build/welcome.ij
Welcome to the Garden Club
Meetings are the first Saturday of each month, 9 a.m., at the north gate.
<<<<<<< .i
-- New members get a starter plot near the shed. Bring gloves; we have tools.
-? Should we mention the waiting list for the larger plots?
=======
New members get a starter plot near the shed. Bring gloves; we lend tools.
Larger plots have a waiting list. Ask at any meeting to join it.
>>>>>>> .j
Questions go to the club secretary.
```

The AI asked whether to mention the waiting list; the author answered by
writing it in, and changed "have" to "lend". The `.ij` is a record of
those decisions, and `ijk_files.py split` turns it back into the two
original files, byte for byte.

**Who it helps:** an editor reviewing AI-assisted work, or anyone who
later needs to know which words were the author's call.

## 4. Is it still what was approved?

A `.ijk` keeps all three versions in one file: the draft, the confirmed
text, and the data. `check` tests that they agree:

```console
$ python3 ijk_files.py pack examples/club/welcome.i examples/club/welcome.j build/corpus/welcome.k -o build/welcome.ijk
wrote build/welcome.ijk
$ python3 ijk_files.py check build/welcome.ijk
k says what j says: yes, exactly
j against i: 1 place(s) differ -- a person decides if they say the same thing
```

The first line is checked by machine: the `.k`, run in K, must hold
exactly the `.j`. The second is left to a person: the draft and the final
text differ in one place, and only a reader can say whether the meaning
changed.

Now change one word in the data, as a buggy converter or a careless edit
might, and check again:

```console
$ sed '/^`title/s/we lend tools/we sell tools/' build/welcome.ijk > build/edited.ijk
$ python3 ijk_files.py check build/edited.ijk
k says what j says: NO
j against i: 1 place(s) differ -- a person decides if they say the same thing
```

**Who it helps:** anyone handing text to another program, another
person or an AI and needing proof it arrived unchanged.

## 5. Ask questions of the whole collection

`feed.py` loads every confirmed document into one K program, where
`docs` holds each document and `corpus` holds them all as columns.
`candidate_ops.k` adds a few operations on top:

```console
$ python3 feed.py build/corpus/ -e 'corpus`title'
("Watering Schedule"
 "Welcome to the Garden Club")
$ python3 feed.py build/corpus/ --prelude candidate_ops.k -e 'find["tools"]'
,"welcome"
$ python3 feed.py build/corpus/ --prelude candidate_ops.k -e 'marked["-?"]'
1 0
```

`find` names the documents containing a phrase. `marked` counts, per
document, the lines starting with a marker: `watering` still carries one
`-?` question, `welcome` none. These operations are a starting point, not
a settled set; `OPERATIONS.md` says why.

## 6. Drafts stay out

A corpus holds confirmed words only. Drafts can contain things an author
never agreed to, so `feed.py` refuses a `.i` outright:

```console
$ python3 feed.py examples/club/plot-rules.i
plot-rules.i: the .i side never goes in a corpus
```

Given a folder, it takes each document's confirmed version (a `.k`,
`.ijk` or `.j`) and names every document it found only as a draft:

```console
$ python3 feed.py examples/club/ -e 'corpus`title'
skipped plot-rules.i: the .i side never goes in a corpus
skipped watering.i: the .i side never goes in a corpus
,"Welcome to the Garden Club"
```

`welcome` goes in from `welcome.j`. `watering` stays out: its draft was
accepted in section 2, but the confirmed copy went to `build/corpus/`,
not into this folder. The feed doesn't guess that a draft was approved.

**Who it helps:** anyone giving a collection of documents to an AI or a
search tool, who wants only the approved versions to go in.

## 7. Look at it in a browser

The viewer puts K and the collection into one HTML file that works
offline: a list of documents, the exact text of each, and a box for K
queries:

```console
$ python3 viewer/build_viewer.py build/corpus/ --prelude candidate_ops.k -o build/club.html
wrote build/club.html (2 document(s))
```

Open `build/club.html` and try `find["plot"]` in the query box.

## Try it on your own writing

1. Write a `.i`: the first line is the title, the rest is the body. Mark
   anything still open with `---` or `(...)`.
2. Run `python3 pipeline.py yourfile.i` until it passes.
3. Copy it to `yourfile.j` and make it your own.
4. Pack, check, feed and view it as above.

The marker rules in full are in `samples/README.md`.
