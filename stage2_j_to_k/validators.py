"""
.k file validators -- checks that run against already-produced K
source, separate from the transform that generates it. Judah's own
architectural call, 2026-09-14: "The ok->oK rule is defined as one of
the .k file validators," not baked into the transform itself. A
validator can run against transform output or hand-written .k files
equally.

Scope decision, flagged rather than silently assumed: this checks for
the standalone word "ok" in K *source* (comments, bare code) and does
NOT touch content inside string literals. Rationale: a string literal
holds a user's actual quoted prose (compiled from their .j content);
silently rewriting words inside it would be altering documented
content, a materially bigger and more sensitive act than normalizing
a code-level reference to the tool. If "ok" needs normalizing inside
quoted prose too, that's a real, separate design decision -- not
assumed here.
"""

import re
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    line: int
    col: int
    message: str


_OK_WORD = re.compile(r"\bok\b")


def find_ok_casing_issues(k_source: str) -> list:
    """
    Scans .k source for the standalone word "ok" outside of string
    literals, and reports each as an issue (should be "oK").
    Correctly tracks string boundaries (including \" escapes) so
    content inside quotes is never flagged.
    """
    issues = []
    for line_no, line in enumerate(k_source.splitlines(), start=1):
        in_string = False
        i = 0
        # Build a mask of which character positions are "outside a
        # string" so the regex search only runs against those spans.
        outside_spans = []
        span_start = 0
        while i < len(line):
            ch = line[i]
            if ch == "\\" and in_string:
                i += 2  # skip the escaped character entirely
                continue
            if ch == '"':
                if not in_string:
                    outside_spans.append((span_start, i))
                    in_string = True
                else:
                    in_string = False
                    span_start = i + 1
            i += 1
        if not in_string:
            outside_spans.append((span_start, len(line)))

        for start, end in outside_spans:
            segment = line[start:end]
            for m in _OK_WORD.finditer(segment):
                issues.append(
                    ValidationIssue(
                        line=line_no,
                        col=start + m.start() + 1,
                        message="lowercase 'ok' should be 'oK'",
                    )
                )
    return issues


def fix_ok_casing(k_source: str) -> str:
    """
    Applies the ok -> oK normalization to every issue found by
    find_ok_casing_issues -- rewrites only the flagged, out-of-string
    occurrences, leaves everything else (including string contents)
    untouched.
    """
    lines = k_source.splitlines(keepends=True)
    issues = find_ok_casing_issues(k_source)
    # Apply right-to-left per line so earlier column offsets on the
    # same line don't shift before they're used.
    by_line = {}
    for issue in issues:
        by_line.setdefault(issue.line, []).append(issue.col)
    for line_no, cols in by_line.items():
        line = lines[line_no - 1]
        for col in sorted(cols, reverse=True):
            idx = col - 1
            line = line[:idx] + "oK" + line[idx + 2:]
        lines[line_no - 1] = line
    return "".join(lines)


def validate(k_source: str) -> list:
    """Runs every registered validator. Currently just the one rule;
    the list return type is deliberate so more validators can be
    added without changing the calling convention."""
    return find_ok_casing_issues(k_source)
