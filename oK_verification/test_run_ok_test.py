"""
Proving the harness itself works -- against the real interpreter,
both a genuine pass and a genuine failure, so a false-positive
"everything's ok" isn't possible.
"""

from run_ok_test import run_k, assert_k_ok


def test_real_success_detected():
    result = run_k("+/1 2 3 4 5")
    assert result.ok, result.stdout
    assert "15" in result.stdout


def test_bare_oK_sentinel_evaluates_with_prelude():
    result = run_k("oK")
    assert result.ok, result.stdout
    assert result.errors == []


def test_bare_oK_fails_without_prelude():
    """Confirms the prelude is actually doing something, not just
    present -- without it, oK is genuinely undefined."""
    result = run_k("oK", use_prelude=False)
    assert not result.ok
    assert any("has not been defined" in e for e in result.errors)


def test_real_error_is_detected_not_missed():
    """The harness's whole job -- make sure a genuine K error
    doesn't slip through as a false pass."""
    result = run_k("{[x]x+1}[3;4]")  # valence error -- too many args
    assert not result.ok
    assert any("error" in e for e in result.errors)


def test_assert_k_ok_raises_on_real_error():
    try:
        assert_k_ok("undefinedThing")
        assert False, "should have raised"
    except AssertionError as e:
        assert "has not been defined" in str(e)


def test_assert_k_ok_passes_silently_on_success():
    assert_k_ok("+/1 2 3")  # no exception


def test_every_error_shape_is_detected():
    """One real trigger per error message oK.js can throw. Before the
    patterns were anchored to line starts, the first four of these
    passed the harness silently."""
    triggers = {
        "(1;2": "parse error.",
        "\u00a7": "unexpected character",
        "a:": "noun expected",
        "1[2]": "function or list expected",
        "1 2+1 2 3": "length error.",
        "{x}[1;2;3]": "valence error.",
        "undefinedThing": "has not been defined",
    }
    for source, expected in triggers.items():
        result = run_k(source, use_prelude=False)
        assert not result.ok, f"{source!r} passed: {result.stdout}"
        assert any(expected in e for e in result.errors), (source, result.errors)


def test_string_value_mentioning_an_error_is_not_a_failure():
    """A string that merely contains error-shaped text is a value, and
    oK prints it starting with a quote, so it must not trip the
    patterns."""
    for source in ['"parse error. x expected."', '"the name \'x\' has not been defined."']:
        result = run_k(source, use_prelude=False)
        assert result.ok, (source, result.errors)


if __name__ == "__main__":
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
