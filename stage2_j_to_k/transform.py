"""
Stage 2 of the ijk pipeline: .j -> .k.

Deliberately minimal, not a solved compiler. The real open question --
what it actually means to "compile" prose (an identity document, not
an arithmetic expression) into K -- is not answered here. What this
does: represent a .j file's content as real K *data*, a dict of
title/body, verified valid against the actual oK interpreter. Nothing
here claims the result is "executable" in any deeper sense than "a K
program that holds this document's content and parses cleanly."

Syntax confirmed directly against oK before writing this, not assumed:
string escaping (`\"`, `\n`, `\\`) matches C-style conventions; dict
literal is `` `key1`key2!(val1;val2) ``; `d[`key]` does lookup.

Lossless as of 2026-10-02. `title`/`body` are a view (first line,
then the rest, stripped); `text` holds the source exactly. Before
`text` existed, 19 of 20 real files lost a trailing newline or the
blank line after the title, and nothing checked for it. Carriage
return and backslash are spliced in by character code rather than
written inside a string literal; `_SPLICED` below says why.
"""

import re
from pathlib import Path


def escape_k_string(text: str) -> str:
    """
    Escapes a Python string for use inside a K string literal.
    Order matters: backslash first, or the escapes just added would
    themselves get re-escaped.
    """
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    text = text.replace("\n", "\\n")
    return text


# Characters oK can't be trusted to read back from a string literal,
# spliced in by code instead. CR: no escape exists and a raw one breaks
# oK's line-based parser. Backslash: oK undoes escapes one kind at a
# time, `\\` first (oK.js, `EC` table), so the `\\n` that correctly
# means "backslash, then n" becomes `\n` and then a newline. Found on a
# real file that writes about `\r\n`.
_SPLICED = {"\r": 13, "\\": 92}
_SPLIT = re.compile("([" + re.escape("".join(_SPLICED)) + "])")


def _utf16_len(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def k_string(text: str) -> str:
    """
    A K expression that evaluates to exactly `text` as a char list.
    One character is enlisted (`,"a"`), since a bare `"a"` is an atom
    in K, not a one-item list. "One character" is counted as oK counts,
    in UTF-16 units: an emoji is two, already a list, and enlisting it
    would nest it (a lone emoji once compiled to `,"😀"`, a list holding
    a string).
    """
    if not _SPLIT.search(text):
        literal = f'"{escape_k_string(text)}"'
        return "," + literal if _utf16_len(text) == 1 else literal
    parts = [
        f"(`c${_SPLICED[p]})" if p in _SPLICED else f'"{escape_k_string(p)}"'
        for p in _SPLIT.split(text)
        if p
    ]
    return "(" + ",".join(parts) + ")" if len(parts) > 1 else "," + parts[0]


def j_to_k(j_file_path: str) -> str:
    """
    Reads a .j file and returns K source: a dict with `title (the
    file's own first line), `body (everything after it, blank lines at
    the top stripped) and `text (the whole file, exactly).
    """
    path = Path(j_file_path)
    text = path.read_text(encoding="utf-8", newline="")
    lines = text.splitlines()

    title = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip()

    values = ";".join(k_string(v) for v in (title, body, text))
    return f"`title`body`text!({values})\n"


def compile_j_to_k(j_file_path: str, k_file_path: str) -> str:
    """Writes the .k output to disk, returns the K source generated."""
    k_source = j_to_k(j_file_path)
    Path(k_file_path).write_text(k_source, encoding="utf-8")
    return k_source
