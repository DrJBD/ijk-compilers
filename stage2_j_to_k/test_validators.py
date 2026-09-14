"""Real tests for the .k file validators."""

import sys
from validators import find_ok_casing_issues, fix_ok_casing, validate


def test_lowercase_ok_in_comment_is_flagged():
    issues = find_ok_casing_issues("/ run this with ok please\noK:1")
    assert len(issues) == 1
    assert issues[0].line == 1


def test_ok_inside_string_literal_is_not_flagged():
    """The core scope decision -- quoted prose content is never
    rewritten, only code-level references."""
    issues = find_ok_casing_issues('x:"that sounds ok to me"')
    assert issues == []


def test_word_boundary_does_not_false_positive_on_substrings():
    """"book", "token", "looked" all contain "ok" -- none should
    trigger."""
    issues = find_ok_casing_issues("/ book token looked")
    assert issues == []


def test_already_correct_oK_is_not_flagged():
    issues = find_ok_casing_issues("oK:1\noK")
    assert issues == []


def test_mixed_line_flags_only_the_out_of_string_occurrence():
    src = 'x:"ok inside string"\n/ ok outside string'
    issues = find_ok_casing_issues(src)
    assert len(issues) == 1
    assert issues[0].line == 2


def test_fix_rewrites_only_flagged_occurrences():
    src = 'x:"ok inside string"\n/ ok outside string'
    fixed = fix_ok_casing(src)
    assert 'x:"ok inside string"' in fixed  # untouched
    assert "/ oK outside string" in fixed   # fixed
    assert find_ok_casing_issues(fixed) == []  # now clean


def test_escaped_quote_inside_string_does_not_break_boundary_tracking():
    """A \\" inside a string shouldn't be mistaken for the string's
    closing quote."""
    src = 'x:"a quote \\" then ok outside"\n/ ok for real'
    issues = find_ok_casing_issues(src)
    # Both "ok"s are actually inside the one string in src's first
    # line (the \" doesn't close it) -- only line 2's is real.
    assert len(issues) == 1
    assert issues[0].line == 2


def test_validate_matches_find_ok_casing_issues():
    src = "/ ok"
    assert validate(src) == find_ok_casing_issues(src)


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
