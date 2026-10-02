Operations on an ijk feed
----

.ijk files are rosetta stones with the same thing said three different ways. This is 
a definition that can easily be shown to be true or false given a review by a human.

-- Claude: now checkable. ijk_files.py check NAME.ijk does the k-to-j half mechanically (oK must hold exactly the j text) and reports the j-to-i half for a person: how many places differ, and with --show, those places as a .ij.

-- What exists: feed.py loads any mix of .i, .j, .k and .ijk files into one oK program. It defines docs (each document's own .k dict) and corpus (the same documents as columns: name, title, body, text). The output of a run is also, can also, be 
reviewed by an AI or the human user.

-- Transport is exact: Every document's text is checked code by code inside oK.

-- Candidate operations, in candidate_ops.k, each checked against Python: lines, starts, has, byname, nlines, marked, find. They're what a real 20-file corpus asked for first when I tried it (how big, which markers, where a word appears, one document by name). -- That's a starting point, not a claim they're the right set.

-- What oK doesn't give us: There's no substring search (ss). ? can't find a string in a list of strings. A one-character string is an atom, not a list. Take wraps around, so 3#"-" is "---". And #' (count each) must be written {#x}'.

-- Why five times is a good place to start.
   What's the first question you want to ask of a corpus? 
   The operation set could grow from real questions, the way the .jmd grammar 
   grew from real letters.

-- Claude: I read "Why five times" as the Five Whys: ask why, then ask why of the answer, five rounds deep. Here, oK answers the what (counts, matches, where). A reviewer, AI or human, reads the output and asks the next why. Any round can need an operation we don't have yet, and that's how the set grows.
-? What's the first why, and of which context?

-- What makes up a corpus?
   A context.  AI have contexts and human conversations have contexts.

-- Claude: then a feed is a context: the documents one conversation is working with, loaded together. feed.py builds one from the files it's given. Nothing names or saves a context yet.

-- The corpus should not carry the .i side as well (drafts, open questions) as 
   identities must be preserved.  Unfortunately there are leaks from triangulation
   which is a known risk and must be minimized.

-- Claude: done. feed.py refuses .i and .ij files, takes only the k or j section of a .ijk, and skips a folder's .i files, naming them on stderr. Tests check that .i text never reaches a feed.

-- Where should operations live? -- Explain?

-- Claude: the question was where an operation's code sits. Today it's K (candidate_ops.k), run inside oK after the feed, so a reviewer sees the operation and its result in one language, and it works in browser oK too. The other place is Python, run before the feed, with oK holding only the answers. That's easier for text, since oK has no substring search, but then oK is a store rather than where the work happens. My recommendation: K inside oK, with Python only for what oK can't do, and named as such.

-? Should results come back out of oK, and if so, as what? -- What results come out of oK when it's run?

-- Claude: today, only text on stdout. `node repl.js feed.k` prints the last expression's value in K's printed form; the interactive REPL prints every line's value. On an error, the REPL prints the message as an ordinary line, and file mode crashes Node (exit 1). oK can also write files itself (`x 0: y`), which nothing here uses yet. So a run's result is K-printed text, which is what an AI or a person reviews.
-? Line 2 is "----". The marker rules read it as a blocking --- question (content "-"), so this file isn't ready. Markdown would read it as a divider, the way a bare --- already is. Which did you mean?
