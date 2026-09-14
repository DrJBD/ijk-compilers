"""
Real tests for stage 1, run with: python3 -m pytest test_transform.py
(or python3 test_transform.py -- includes a bare-assert fallback
runner at the bottom so this works with no dependencies installed.)
"""

import tempfile
from pathlib import Path

from markers import classify_line, BLOCKING, NONBLOCKING
from transform import check_readiness, promote


def test_ready_file_has_no_blocking_lines():
    text = (
        "Sample Title\n"
        "\n"
        "-- Context --\n"
        "-- A statement. -- An aside -- another aside.\n"
        "- Confirmed, no open questions here.\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".i", delete=False) as f:
        f.write(text)
        path = f.name
    report = check_readiness(path)
    assert report.ready, report.summary()
    assert report.blocking == []


def test_triple_dash_blocks():
    text = "--- Still deciding whether this belongs here.\n"
    with tempfile.NamedTemporaryFile("w", suffix=".i", delete=False) as f:
        f.write(text)
        path = f.name
    report = check_readiness(path)
    assert not report.ready
    assert report.blocking[0][1] == "---"


def test_bare_question_blocks():
    text = "? did this actually get answered, unclear\n"
    with tempfile.NamedTemporaryFile("w", suffix=".i", delete=False) as f:
        f.write(text)
        path = f.name
    report = check_readiness(path)
    assert not report.ready
    assert report.blocking[0][1] == "?"


def test_paren_ellipsis_reduces_to_triple_dash():
    """The rule from Judah's own example, 2026-09-14: (...) blocks
    the same way --- does."""
    text = "Whatever medium this actually works in (...) still open.\n"
    with tempfile.NamedTemporaryFile("w", suffix=".i", delete=False) as f:
        f.write(text)
        path = f.name
    report = check_readiness(path)
    assert not report.ready
    assert report.blocking[0][1] == "(...)"


def test_paren_ellipsis_found_mid_line_not_just_line_initial():
    """Deliberately checking the flagged assumption: (...) is NOT
    restricted to line-initial, unlike every other marker."""
    marker, status = classify_line("Some prose, then (...) more prose.")
    assert marker == "(...)"
    assert status == BLOCKING


def test_bare_triple_dash_is_a_divider_not_a_blocking_marker():
    """Real bug found testing against a real identity file: four bare '---'
    section dividers were false-positived as blocking questions.
    A bare --- has no question attached to it; the marker's own
    definition requires real content following it on the line."""
    marker, status = classify_line("---")
    assert status != BLOCKING, (marker, status)


def test_dash_dash_mid_line_is_not_a_marker():
    """The position rule this all inherits: -- only triggers when
    it's the first thing on the line."""
    marker, status = classify_line("Ordinary prose -- with an aside.")
    assert marker is None
    assert status is None


def test_promote_refuses_when_not_ready():
    text = "--- open question here\n"
    with tempfile.NamedTemporaryFile("w", suffix=".i", delete=False) as f:
        f.write(text)
        i_path = f.name
    j_path = i_path.replace(".i", ".j")
    try:
        promote(i_path, j_path)
        assert False, "should have raised"
    except ValueError as e:
        assert "not ready" in str(e)
    assert not Path(j_path).exists()


def test_promote_succeeds_when_ready():
    text = "- Confirmed content, nothing open.\n"
    with tempfile.NamedTemporaryFile("w", suffix=".i", delete=False) as f:
        f.write(text)
        i_path = f.name
    j_path = i_path.replace(".i", ".j")
    report = promote(i_path, j_path)
    assert report.ready
    assert Path(j_path).read_text(encoding="utf-8") == text
    Path(j_path).unlink()


if __name__ == "__main__":
    # No-dependency fallback: run every test_* function directly.
    import sys

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
