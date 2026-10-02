"""
Real tests for pipeline.py, run against the real oK interpreter like
every other suite here. Run from the repo root: python3 test_pipeline.py
"""

import sys
import tempfile
from pathlib import Path

import pipeline


def _write(text: str, suffix: str) -> Path:
    with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8", newline="") as f:
        f.write(text)
        return Path(f.name)


def test_ready_i_file_passes_every_stage():
    path = _write('Title\n-- Context --\nA "quoted" line, a back\\slash, an em dash — done.', ".i")
    result = pipeline.run_pipeline(path)
    assert result.ok, result.summary()
    assert result.passed == pipeline.STAGES


def test_blocking_marker_stops_at_readiness_and_runs_nothing_else():
    path = _write("Title\n--- what do you recommend here?\n", ".i")
    result = pipeline.run_pipeline(path)
    assert result.failed_at == "readiness"
    assert result.passed == []
    assert result.k_source is None


def test_j_file_skips_the_readiness_check():
    # A .j file has already been promoted; a stray marker in it is
    # content now, not a question, so stage 1 doesn't re-run.
    path = _write("Title\n--- left in on purpose\n", ".j")
    result = pipeline.run_pipeline(path)
    assert result.ok, result.summary()


def test_in_repo_fixture_passes():
    fixture = Path(__file__).parent / "stage2_j_to_k" / "fixtures" / "identity_sample.i"
    assert pipeline.run_pipeline(fixture).ok


def test_round_trip_catches_a_compile_that_drops_content():
    # Proves the round-trip stage can fail: swap in a stage 2 that
    # loses the last character of the body. It still evaluates in oK,
    # so only the round-trip check can see the loss.
    path = _write("Title\nBody text.", ".i")
    real = pipeline._stage2.j_to_k
    pipeline._stage2.j_to_k = lambda p: real(p).replace('."', '"')
    try:
        result = pipeline.run_pipeline(path)
    finally:
        pipeline._stage2.j_to_k = real
    assert "evaluate" in result.passed
    assert result.failed_at == "round-trip", result.summary()


def test_out_dir_gets_j_and_k_and_source_is_untouched():
    src = _write("Title\nBody.", ".i")
    before = src.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as out:
        code = pipeline.main([str(src), "--out", out])
        assert code == 0
        assert (Path(out) / f"{src.stem}.j").read_text(encoding="utf-8") == before
        assert (Path(out) / f"{src.stem}.k").exists()
    assert src.exists() and src.read_text(encoding="utf-8") == before


def test_crlf_and_emoji_file_round_trips_and_out_copy_is_byte_exact():
    src = _write("Title \u2014 \U0001F600\r\n\r\nBody\r\n", ".i")
    raw = src.read_bytes()
    result = pipeline.run_pipeline(src)
    assert result.ok, result.summary()
    with tempfile.TemporaryDirectory() as out:
        assert pipeline.main([str(src), "--out", out]) == 0
        assert (Path(out) / f"{src.stem}.j").read_bytes() == raw


def test_round_trip_catches_lost_whitespace():
    # The loss stage 2 used to have: title/body still match, but the
    # file's trailing newline is gone from `text.
    path = _write("Title\nBody.\n", ".i")
    real = pipeline._stage2.j_to_k
    pipeline._stage2.j_to_k = lambda p: real(p).replace('Body.\\n")', 'Body.")')
    try:
        result = pipeline.run_pipeline(path)
    finally:
        pipeline._stage2.j_to_k = real
    assert result.failed_at == "round-trip", result.summary()


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
