/ Candidate operations on an ijk feed -- not settled; see OPERATIONS.md.
/ Load after a feed: python3 feed.py DIR --prelude candidate_ops.k
/ Each one is checked against Python in test_feed.py.
/ --
/ Three oK traps these work around. A one-character string is an atom,
/ not a list, so patterns are enlisted with (),. Split fails on such an
/ atom, so lines enlists too. And take wraps around: 3#"-" is "---", so
/ a prefix test checks the length first.

/ lines of a text; prefix test; substring test (oK has no ss)
lines:{"\n"\(),x}
starts:{y:(),y; $[(#y)>#x;0;y~(#y)#x]}
has:{[s;p] p:(),p; i:&s=*p; i:i@&i<1+(#s)-#p; 0<+/p~/:(#p)#'i_\:s}

/ a document by name: byname`hello
byname:(`$corpus`name)!docs

/ per-document counts: lines, and lines starting with a given marker
nlines:{#lines x}'corpus`text
marked:{[m] {[m;t] +/{starts[x;y]}[;m]'lines t}[m]'corpus`text}

/ names of the documents whose text contains a pattern
find:{corpus[`name]@&{has[x;y]}[;x]'corpus`text}
