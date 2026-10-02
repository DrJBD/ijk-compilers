Operations on an ijk feed
-- Draft by Claude, for Judah to edit. Nothing here is settled: answer inline, cut, or add.

-- What exists. feed.py loads any mix of .i, .j, .k and .ijk files into one oK program. It defines docs (each document's own .k dict) and corpus (the same documents as columns: name, title, body, text). Transport is exact: every document's text is checked code by code inside oK.

-- Candidate operations, in candidate_ops.k, each checked against Python: lines, starts, has, byname, nlines, marked, find. They're what a real 20-file corpus asked for first when I tried it (how big, which markers, where a word appears, one document by name). That's a starting point, not a claim they're the right set.

-- What oK doesn't give us, each of which bit while writing the candidates. There's no substring search (ss). ? can't find a string in a list of strings. A one-character string is an atom, not a list. Take wraps around, so 3#"-" is "---". And #' (count each) must be written {#x}'.

-? What's the first question you want to ask of a corpus? The operation set could grow from real questions, the way the .jmd grammar grew from real letters.
-? What makes up a corpus?
-? Should a corpus carry the .i side as well (drafts, open questions), or only what reached .k?
-? Where should operations live?
-? Should results come back out of oK, and if so, as what?
