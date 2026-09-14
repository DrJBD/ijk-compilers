"""
.jmd marker grammar, as confirmed in JMD_GRAMMAR_AND_PAGES_NOTES.md,
reused here as the readiness check for stage 1 (.i -> .j).

Five markers, one column of meaning each. Position rule, confirmed
there: line-initial only. `-`, `--`, `---`, `-?`, and bare `?` only
trigger as markers when they're the first thing on a line; the same
characters anywhere else are ordinary text.

    -    approved, ready                         -- doesn't block
    --   ordinary draft paragraph, not reviewed   -- doesn't block
    ---  "I want your recommendation"             -- BLOCKS
    -?   inline question, either party can ask    -- doesn't block
    ?    AI reviewed a -? and can't confirm it     -- BLOCKS
         was actually answered

New rule, Judah's own example, 2026-09-14: "(...)" reduces to "---".
A parenthesized ellipsis is a common, natural way to mark "there's
more here, unfinished" in ordinary prose -- treated as an alias for
the same blocking marker, not a new fifth thing to track separately.

Open design question, not yet confirmed: unlike the other markers,
"(...)" is checked anywhere on the line, not line-initial-only. The
original position rule existed specifically because the author's own
habitual writing uses mid-sentence "--" constantly (52 times in one
real file); "(...)" is a much less common, more distinctive token, so
restricting it to line-initial felt like it would miss real cases
without preventing real collisions. Flagged here as an assumption,
not a settled decision -- easy to tighten to line-initial-only later
if a real file shows it colliding with ordinary prose.
"""

import re

BLOCKING = "BLOCKING"
NONBLOCKING = "NONBLOCKING"

# Order matters -- longest/most specific marker checked first, so "---"
# isn't misread as "--" plus a stray "-", and "-?" isn't misread as "-".
_LINE_INITIAL_MARKERS = [
    ("-?", NONBLOCKING),
    ("--", NONBLOCKING),
    ("-", NONBLOCKING),
]

_BARE_QUESTION = re.compile(r"^\?(\s|$)")
_PAREN_ELLIPSIS = re.compile(r"\(\s*\.\.\.\s*\)")
# "---" only counts as the blocking marker when real content follows it
# on the same line -- a bare "---" is a markdown section divider, a
# real collision found by testing against a real identity file (four false
# positives: lines that were only ever "---" with nothing after them,
# not "I want your recommendation" questions). Every other marker's
# own definition tolerates being bare; this one's doesn't, since its
# whole meaning is "here is a question," not "here is a divider."
_TRIPLE_DASH_WITH_CONTENT = re.compile(r"^---\s*\S")


def classify_line(line: str):
    """
    Returns (marker, status) for one line of a .i/.jmd file.
    marker is one of "-", "--", "---", "-?", "?", "(...)", or None.
    status is BLOCKING, NONBLOCKING, or None if no marker present.
    """
    stripped = line.lstrip()

    if _BARE_QUESTION.match(stripped):
        return "?", BLOCKING

    if _TRIPLE_DASH_WITH_CONTENT.match(stripped):
        return "---", BLOCKING

    for marker, status in _LINE_INITIAL_MARKERS:
        if stripped.startswith(marker):
            return marker, status

    if _PAREN_ELLIPSIS.search(line):
        return "(...)", BLOCKING

    return None, None


def find_blocking_lines(text: str):
    """
    Returns a list of (line_number, marker, line_text) for every
    blocking marker found -- the actual readiness check for stage 1.
    An .i file with zero blocking lines is ready to become .j.
    """
    blocking = []
    for i, line in enumerate(text.splitlines(), start=1):
        marker, status = classify_line(line)
        if status == BLOCKING:
            blocking.append((i, marker, line))
    return blocking
