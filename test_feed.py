"""
Tests for feed.py and candidate_ops.k, against the real oK.
Run from the repo root: python3 test_feed.py
"""

import sys
import tempfile
from pathlib import Path

import feed
import ijk_files
import pipeline

ROOT = Path(__file__).parent
OPS = (ROOT / "candidate_ops.k").read_text(encoding="utf-8")


def _run(feed_text: str, expr: str) -> str:
    result = pipeline._ok.run_k_file(feed_text + expr)
    assert result.ok, result.errors
    return result.stdout.strip()


def _corpus(texts: dict) -> Path:
    d = Path(tempfile.mkdtemp())
    for name, text in texts.items():
        (d / f"{name}.j").write_text(text, encoding="utf-8", newline="")
    return d


# Built to hit what went wrong while writing the ops: lines shorter
# than the marker ("-", "--"), one-character patterns, a pattern at the
# very end of a text, CRLF, and text with no newline at all.
EDGE = {
    "a": "Alpha\n-\n--\n- set\n-- draft\n-? ask\n--- want\nI am here\ni AM too\nend.",
    "b": "Beta\r\n- crlf line\r\nno marker\r\n",
    "c": "Gamma",
    "d": "Delta\n— dash \U0001F600\nends with xy",
}


def test_every_document_arrives_exactly():
    files = feed.collect([str(ROOT / "samples"), str(_corpus(EDGE))])
    text = feed.build_feed(files)
    got = _run(text, ",/{(#x;+/x;+/(1+!#x)*x)}'0+'corpus`text").split()
    expected = []
    for f in files:
        source = f.read_text(encoding="utf-8", newline="") if f.suffix != ".k" else None
        if source is None:  # a sample .k: compare against what it was built from
            j = f.with_suffix(".j")
            source = j.read_text(encoding="utf-8", newline="")
        expected.extend(str(n) for n in pipeline._fingerprint(source))
    assert got == expected


def test_single_document_feed():
    text = feed.build_feed([ROOT / "samples" / "hello.k"])
    assert _run(text, "corpus`name") == ',"hello"'


def test_ijk_uses_its_k_or_compiles_its_j():
    d = Path(tempfile.mkdtemp())
    j = b"Title\nBody.\n"
    k = pipeline._stage2.j_to_k(str(_corpus({"x": j.decode()}) / "x.j")).encode()
    (d / "with.ijk").write_bytes(ijk_files.pack_ijk({"i": ("with.i", j), "j": ("with.j", j), "k": ("with.k", k)}))
    (d / "without.ijk").write_bytes(ijk_files.pack_ijk({"i": ("without.i", j), "j": ("without.j", j)}))
    text = feed.build_feed(feed.collect([str(d)]))
    assert _run(text, "corpus`title") == '("Title"\n "Title")'


def test_directory_prefers_k_then_ijk_then_j_then_i():
    picked = {f.stem: f.suffix for f in feed.collect([str(ROOT / "samples")])}
    assert picked == {"escapes": ".k", "hello": ".k", "revised": ".k"}


def test_not_ready_file_is_refused():
    try:
        feed.build_feed([ROOT / "samples" / "src" / "open.i"])
    except ValueError as e:
        assert "readiness" in str(e)
        return
    raise AssertionError("fed a file that isn't ready")


def test_candidate_ops_match_python():
    files = feed.collect([str(_corpus(EDGE))])
    texts = [f.read_text(encoding="utf-8", newline="") for f in files]
    text = feed.build_feed(files) + OPS
    lines = [t.split("\n") for t in texts]

    assert _run(text, "nlines").split() == [str(len(l)) for l in lines]
    for m in ["-", "--", "---", "- ", "-- ", "-? ", "?"]:
        expected = [str(sum(x.startswith(m) for x in l)) for l in lines]
        assert _run(text, f'marked["{m}"]').split() == expected, m
    for p in ["a", ".", "end.", "xy", "I am", "—", "\U0001F600", "zz", "crlf"]:
        expected = [str(int(p in t)) for t in texts]
        assert _run(text, f'{{has[x;"{p}"]}}\'corpus`text').split() == expected, p
    assert _run(text, 'find["crlf"]') == ',,"b"'  # a list of one one-letter name
    assert _run(text, "(byname`b)`title") == '"Beta"'


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
