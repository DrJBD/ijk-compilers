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

There are three examples, all run from the repo root. The first,
three documents for a neighbourhood garden club (`examples/club/`), goes
through every tool once. The second, a recipe passed back and forth
between a cook and an AI (`examples/recipe/`), follows one document
through several rounds of review. The third, a shop's returns policy
(`examples/shop/`), is the business case: a draft that needs legal
sign-off, and published copies that must match what was signed.

Every command's output on this page is real: `test_examples.py` runs each
one and fails if the page and the tools disagree. Files the examples
write go in `build/`, which git ignores. You need Python 3, Node and a
clone of oK (see `README.md`).

## The garden club

### 1. Is it ready to send?

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

### 2. Confirm, then compile

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

### 3. What did the author decide?

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

### 4. Is it still what was approved?

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

### 5. Ask questions of the whole collection

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

### 6. Drafts stay out

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

### 7. Look at it in a browser

The viewer puts K and the collection into one HTML file that works
offline: a list of documents, the exact text of each, and a box for K
queries:

```console
$ python3 viewer/build_viewer.py build/corpus/ --prelude candidate_ops.k -o build/club.html
wrote build/club.html (2 document(s))
```

Open `build/club.html` and try `find["plot"]` in the query box.

## A recipe, back and forth

A cook writes up a recipe with an AI's help. It takes three rounds, kept
in `examples/recipe/` as `round-1.i`, `round-2.i` and `shakshuka.i`.

### 8. A question can pass without being answered

The AI's first draft. Its question about the oven is a `-?`, which
doesn't block, so this round passes:

```console
$ cat examples/recipe/round-1.i
Shakshuka for Four
Warm 2 tbsp olive oil in a wide pan. Add 1 onion and 1 jalapeño, diced.
-- Stir in 2 tsp cumin, 1 tsp paprika and ½ tsp chili flakes, then 800 g crushed tomatoes.
-- Simmer 10 minutes, make four hollows and crack an egg into each.
-? Lid on the pan, or into a 200 °C oven?
Serve with crème fraîche and bread. 🍳
```

The cook approves the two draft lines (`--` becomes `-`) but never
answers the question. On its next pass, the AI notices and turns the
`-?` into a bare `?`: "I asked, and I can't tell that it was answered."
A bare `?` blocks:

```console
$ diff examples/recipe/round-1.i examples/recipe/round-2.i
3,5c3,5
< -- Stir in 2 tsp cumin, 1 tsp paprika and ½ tsp chili flakes, then 800 g crushed tomatoes.
< -- Simmer 10 minutes, make four hollows and crack an egg into each.
< -? Lid on the pan, or into a 200 °C oven?
---
> - Stir in 2 tsp cumin, 1 tsp paprika and ½ tsp chili flakes, then 800 g crushed tomatoes.
> - Simmer 10 minutes, make four hollows and crack an egg into each.
> ? Lid on the pan, or into a 200 °C oven? The cook approved the lines around this but didn't answer it.
```

The cook answers it in the text, and the question goes:

```console
$ diff examples/recipe/round-2.i examples/recipe/shakshuka.i
5c5
< ? Lid on the pan, or into a 200 °C oven? The cook approved the lines around this but didn't answer it.
---
> Lid on, low heat, 6 to 8 minutes, until the whites set. No oven needed.
```

All three rounds through the pipeline:

```console
$ python3 pipeline.py examples/recipe/
PASS  round-1.i
FAIL  round-2.i -- stopped at readiness
      round-2.i: NOT ready -- 1 blocking marker(s):
        line 5: [?] ? Lid on the pan, or into a 200 °C oven? The cook approved the lines around this but didn't answer it.
PASS  shakshuka.i

2/3 through to oK
```

Round 1 passes because a `-?` doesn't block: no tool can tell whether a
question was answered somewhere in the text. A reviewer can. The bare `?`
is how the reviewer, human or AI, says "not yet", and from then on the
file can't be promoted until someone answers.

**Who it helps:** anyone reviewing with an AI over several rounds, where
a question can quietly get lost between drafts.

### 9. Every character arrives

The cook accepts the last round as it stands:

```console
$ python3 pipeline.py examples/recipe/shakshuka.i --out build/kitchen/
PASS  shakshuka.i

1/1 through to oK
```

The recipe has accents (jalapeño, crème fraîche), a fraction (½), a
degree sign and an emoji. The PASS above already means the `.k` holds
every one of them exactly, checked character by character in K. Searches
work on them too:

```console
$ python3 feed.py build/kitchen/ --prelude candidate_ops.k -e 'find["crème fraîche"]'
,"shakshuka"
```

K counts text in UTF-16 units, as JavaScript does, so its length differs
from Python's by one: the egg emoji is two units in K and one character
in Python. Nothing is lost; the two just count differently:

```console
$ python3 feed.py build/kitchen/ --prelude candidate_ops.k -e '#byname[`shakshuka;`text]'
359
$ python3 -c 'print(len(open("examples/recipe/shakshuka.i", encoding="utf-8").read()))'
358
```

**Who it helps:** anyone whose writing isn't plain English: names,
other languages, symbols, emoji.

### 10. The whole journey in one file

Pack the AI's first draft with the cook's final text and its data, and
the `.ijk` keeps where the recipe started and where it ended:

```console
$ python3 ijk_files.py pack examples/recipe/round-1.i build/kitchen/shakshuka.j build/kitchen/shakshuka.k -o build/shakshuka.ijk
wrote build/shakshuka.ijk
$ python3 ijk_files.py check --show build/shakshuka.ijk
k says what j says: yes, exactly
j against i: 1 place(s) differ -- a person decides if they say the same thing
Shakshuka for Four
Warm 2 tbsp olive oil in a wide pan. Add 1 onion and 1 jalapeño, diced.
<<<<<<< .i
-- Stir in 2 tsp cumin, 1 tsp paprika and ½ tsp chili flakes, then 800 g crushed tomatoes.
-- Simmer 10 minutes, make four hollows and crack an egg into each.
-? Lid on the pan, or into a 200 °C oven?
=======
- Stir in 2 tsp cumin, 1 tsp paprika and ½ tsp chili flakes, then 800 g crushed tomatoes.
- Simmer 10 minutes, make four hollows and crack an egg into each.
Lid on, low heat, 6 to 8 minutes, until the whites set. No oven needed.
>>>>>>> .j
Serve with crème fraîche and bread. 🍳
```

### 11. Getting the originals back

The `.ijk` isn't a summary. Unpacking it gives back each file byte for
byte:

```console
$ python3 ijk_files.py unpack build/shakshuka.ijk -d build/back/
wrote build/back/round-1.i
wrote build/back/shakshuka.j
wrote build/back/shakshuka.k
$ cmp build/back/round-1.i examples/recipe/round-1.i && echo "round-1.i: identical"
round-1.i: identical
$ cmp build/back/shakshuka.j examples/recipe/shakshuka.i && echo "shakshuka.j: identical to the approved draft"
shakshuka.j: identical to the approved draft
```

**Who it helps:** anyone who has to show, later, exactly what a document
said at each stage, such as a recipe for a cookbook, a policy, or a contract.

## A returns policy: signed off, and provably unchanged

Example Shop (made up) is updating its returns policy. A manager drafts
it with an AI. Legal has to answer one question and sign the final text.
Then the policy goes to the website, the checkout page and the receipt
printer, and every copy has to say exactly what legal signed.

If you use git, this will look familiar, and ijk is meant to sit beside
it: `.i` and `.j` files are plain text and live in a repo like anything
else. git records what changed and who committed it. ijk records two
things git doesn't: whether each part is settled, and proof that a
published copy matches the signed text.

### 12. Nothing ships with an open question

The draft has a question for legal, marked `---`:

```console
$ cat examples/shop/returns-draft.i
Returns Policy
You can return most items to Example Shop for a full refund.
-- Returns are accepted within 30 days of delivery.
-- Bring the item and your receipt to any store, or send it back by post.
--- Legal: do sale items get the same return window?
Refunds go back to the original payment method within 5 working days.
```

The manager writes legal's answer into `returns.i`. Legal then edits and
signs the final text as `returns.j`. The folder holds every stage, and
the pipeline shows which ones could ship:

```console
$ python3 pipeline.py examples/shop/
PASS  receipt-footer.j
FAIL  returns-draft.i -- stopped at readiness
      returns-draft.i: NOT ready -- 1 blocking marker(s):
        line 5: [---] --- Legal: do sale items get the same return window?
PASS  returns.i
PASS  returns.j

3/4 through to oK
```

In a build or release script, the pipeline's exit code is the gate: it
is `0` only when every file passes.

### 13. What legal changed

```console
$ python3 ijk_files.py merge examples/shop/returns.i examples/shop/returns.j -o build/returns.ij
wrote build/returns.ij
$ cat build/returns.ij
Returns Policy
You can return most items to Example Shop for a full refund.
<<<<<<< .i
-- Returns are accepted within 30 days of delivery.
-- Bring the item and your receipt to any store, or send it back by post.
-- Sale items can be exchanged within the same window, but not refunded.
=======
Returns are accepted within 14 days of delivery, as printed on every receipt.
Bring the item and your receipt to any store, or send it back by post.
Sale items can be exchanged within the same window, but not refunded.
>>>>>>> .j
Refunds go back to the original payment method within 5 working days.
```

Legal took off the draft markers, and made one real decision: the draft
said 30 days, but every receipt already printed says 14, so the signed
policy says 14. The block uses git's own conflict markers, so it reads
like a merge conflict, but nothing is in conflict: it is the record of
the sign-off.

### 14. The website says what was signed

Compile the signed texts into the data the website and the checkout page
will load, and pack the policy with its draft and its data:

```console
$ python3 pipeline.py examples/shop/receipt-footer.j examples/shop/returns.j --out build/published/
PASS  receipt-footer.j
PASS  returns.j

2/2 through to oK
$ python3 ijk_files.py pack examples/shop/returns.i examples/shop/returns.j build/published/returns.k -o build/returns.ijk
wrote build/returns.ijk
$ python3 ijk_files.py check build/returns.ijk
k says what j says: yes, exactly
j against i: 1 place(s) differ -- a person decides if they say the same thing
```

Now suppose the website's copy goes back to the draft's 30 days: an old
file reused, a bad copy-paste, a well-meant "fix". The check catches it,
and exits non-zero so a script can stop the release:

```console
$ sed '/^`title/s/14 days/30 days/' build/returns.ijk > build/returns-website.ijk
$ python3 ijk_files.py check build/returns-website.ijk || echo "release stopped"
k says what j says: NO
j against i: 1 place(s) differ -- a person decides if they say the same thing
release stopped
```

### 15. When the policy changes, find every copy that states it

Next year the window changes. Before anyone edits anything, find every
signed text that states the current one:

```console
$ python3 feed.py build/published/ --prelude candidate_ops.k -e 'find["14 days"]'
("receipt-footer"
 "returns")
```

Both need a new round of sign-off. The search is exact, capital letters
included:

```console
$ python3 feed.py build/published/ --prelude candidate_ops.k -e 'find["Sale items"]'
("receipt-footer"
 "returns")
$ python3 feed.py build/published/ --prelude candidate_ops.k -e 'find["sale items"]'
()
```

**Who it helps:** legal and compliance teams signing customer-facing
text, the people who publish it, and the auditor who later asks "show
me that what customers saw is what you approved."

## Try it on your own writing

1. Write a `.i`: the first line is the title, the rest is the body. Mark
   anything still open with `---` or `(...)`.
2. Run `python3 pipeline.py yourfile.i` until it passes.
3. Copy it to `yourfile.j` and make it your own.
4. Pack, check, feed and view it as above.

The marker rules in full are in `samples/README.md`.
