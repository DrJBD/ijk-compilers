"""
Real tests for stage 2, verified against the actual oK interpreter --
same discipline as stage1_i_to_j: no mocked K semantics.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "oK_verification"))
from run_ok_test import run_k, assert_k_ok  # noqa: E402
from transform import escape_k_string, k_string, j_to_k, compile_j_to_k  # noqa: E402


def _write_j(text: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".j", delete=False, newline="") as f:
        f.write(text)
        return f.name


def test_escape_handles_quotes_backslashes_newlines():
    raw = 'a "quote", a \\backslash\\, and a\nnewline'
    escaped = escape_k_string(raw)
    # Round-trip through the real interpreter rather than
    # hand-verifying the escaping logic in isolation.
    result = run_k(f'"{escaped}"')
    assert result.ok, result.stdout
    assert '"a \\"quote\\", a \\\\backslash\\\\, and a\\nnewline"' in result.stdout


def test_simple_j_file_compiles_to_valid_k():
    path = _write_j("Title Line\nBody line one.\nBody line two.")
    k_source = j_to_k(path)
    result = run_k(f"d:{k_source}\nd[`title]\nd[`body]")
    assert result.ok, result.stdout
    assert '"Title Line"' in result.stdout
    assert "Body line one" in result.stdout


def test_identity_style_file_round_trips_through_real_interpreter():
    """An identity-shaped fixture kept in-repo: multi-line, with quotes,
    an apostrophe, an em dash and an ellipsis, so the escaping is
    exercised the way real files exercise it."""
    fixture = Path(__file__).parent / "fixtures" / "identity_sample.i"
    k_source = j_to_k(str(fixture))
    result = run_k(f"d:{k_source}\nd[`title]")
    assert result.ok, result.stdout
    assert '"Sample Identity"' in result.stdout


def test_compile_writes_valid_k_file_to_disk():
    j_path = _write_j("Small\nJust a small body.")
    k_path = j_path.replace(".j", ".k")
    compile_j_to_k(j_path, k_path)
    k_text = Path(k_path).read_text(encoding="utf-8")
    assert_k_ok(f"d:{k_text}\nd[`title]")
    Path(k_path).unlink()


def test_empty_body_still_compiles():
    """A one-line .j file (title, no body) shouldn't break the
    transform or produce invalid K."""
    path = _write_j("Just A Title")
    k_source = j_to_k(path)
    assert_k_ok(f"d:{k_source}\nd[`body]")


def _codes(k_expr: str) -> str:
    """oK's own character codes for a K string expression."""
    result = run_k(f"0+{k_expr}")
    assert result.ok, result.stdout
    # oK prints a one-item list with a leading comma (",13").
    return result.stdout.strip().splitlines()[-1].strip().lstrip(",")


def test_k_string_is_exact_for_awkward_text():
    # Carriage return has no escape in oK and breaks its parser raw;
    # one character must be enlisted to be a list rather than an atom.
    # A literal backslash before n, t or a quote is the case oK's own
    # unescaping order corrupts; see _SPLICED in transform.py.
    for text in ["a\rb", "\r", "line\r\nnext", "x", "", 'tab\there "q" \\ end\n',
                 "\\n", "\\r\\n", '\\"', "\\t", "\\", "\\\\n"]:
        expected = " ".join(str(ord(c)) for c in text)
        got = _codes(k_string(text)) if text else ""
        if text:
            assert got == expected, (text, got)
        assert_k_ok(f"#{k_string(text)}")


def test_text_key_keeps_what_title_and_body_strip():
    # The whitespace 19 of 20 real files lost before `text existed:
    # a blank line after the title and a trailing newline.
    source = "Title\n\nBody.\n"
    path = _write_j(source)
    result = run_k(f"d:{j_to_k(path)}#d[`text]")
    assert result.ok, result.stdout
    assert result.stdout.strip().splitlines()[-1].strip() == str(len(source))


def test_crlf_file_keeps_its_line_endings():
    source = "Title\r\nBody one.\r\nBody two.\r\n"
    path = _write_j(source)
    k_source = j_to_k(path)
    assert _codes(f"(`title`body`text!{k_source.split('!', 1)[1].strip()})[`text]") == " ".join(
        str(ord(c)) for c in source
    )


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
