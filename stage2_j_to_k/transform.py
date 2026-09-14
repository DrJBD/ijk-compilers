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
"""

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


def j_to_k(j_file_path: str) -> str:
    """
    Reads a .j file and returns K source: a dict with `title (the
    file's own first line) and `body (everything after it, blank
    lines at the top stripped).
    """
    path = Path(j_file_path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip()

    k_title = escape_k_string(title)
    k_body = escape_k_string(body)

    return f'`title`body!("{k_title}";"{k_body}")\n'


def compile_j_to_k(j_file_path: str, k_file_path: str) -> str:
    """Writes the .k output to disk, returns the K source generated."""
    k_source = j_to_k(j_file_path)
    Path(k_file_path).write_text(k_source, encoding="utf-8")
    return k_source
