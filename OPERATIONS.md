Operations on an ijk feed
----

.ijk files are rosetta stones with the same thing said three different ways. This is 
a definition that can easily be shown to be true or false given a review by a human.

-- ijk_files.py check NAME.ijk does the k-to-j half mechanically 
   (oK must hold exactly the j text) 
   and reports the j-to-i half for a person: How many places differ?
   Use with --show, those places as a .ij.

-- What exists: feed.py loads any mix of .i, .j, .k and .ijk files into one oK program. It defines docs (each document's own .k dict) and corpus (the same documents as columns: name, title, body, text). The output of a run is also, can also, be 
reviewed by an AI or the human user.

-- Transport is exact: Every document's text is checked code by code inside oK.

-- Candidate operations, in candidate_ops.k, each checked against Python: lines, starts, has, byname, nlines, marked, find. They're what a real 20-file corpus asked for first when I tried it (how big, which markers, where a word appears, one document by name). -- That's a starting point, not a claim they're the right set.

-- What oK doesn't give us: There's no substring search (ss). ? can't find a string in a list of strings. A one-character string is an atom, not a list. Take wraps around, so 3#"-" is "---". And #' (count each) must be written {#x}'.

-- Why five times is a good place to start.
   What's the first question you want to ask of a corpus? 
   The operation set could grow from real questions, the way the .jmd grammar 
   grew from real letters.

-- What makes up a corpus?
   A context.  AI have contexts and human conversations have contexts.

-- The corpus should not carry the .i side as well (drafts, open questions) as 
   identities must be preserved.  Unfortunately there are leaks from triangulation
   which is a known risk and must be minimized.
