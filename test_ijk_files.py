"""
Tests for .ij and .ijk. Run from the repo root: python3 test_ijk_files.py
"""

import random
import sys
import tempfile
from pathlib import Path

import ijk_files
from ijk_files import merge_ij, split_ij, pack_ijk, unpack_ijk

# Pieces chosen to hit what has gone wrong elsewhere in this repo: CR
# and CRLF, a missing final newline, backslash-n written as text,
# "====" lines like the house .i style, non-ASCII, and characters
# str.splitlines would wrongly treat as line breaks.
_PIECES = ["a", "b", "line", "\n", "\r\n", "\r", "\\n", "=" * 60, "---", "—",
           "\U0001F600", "\x0c", " ", "\t", '"', " "]


def _random_text(rng) -> str:
    return "".join(rng.choice(_PIECES) for _ in range(rng.randint(0, 30)))


def _mutate(rng, text: str) -> str:
    lines = text.splitlines(keepends=True) or [""]
    for _ in range(rng.randint(1, 3)):
        k = rng.randrange(len(lines))
        lines[k] = rng.choice(["", _random_text(rng), lines[k] + _random_text(rng)])
    return "".join(lines)


def test_identical_files_merge_to_the_same_text():
    text = "Title\n- settled\n-? asked\n"
    assert merge_ij(text, text) == text


def test_changed_line_shows_both_versions():
    ij = merge_ij("Title\n-? Which one?\nend\n", "Title\nThis one.\nend\n")
    assert ij == "Title\n<<<<<<< .i\n-? Which one?\n=======\nThis one.\n>>>>>>> .j\nend\n"


def test_merge_then_split_is_exact_fuzzed():
    rng = random.Random(20261002)
    for _ in range(2000):
        i = _random_text(rng)
        j = _mutate(rng, i) if rng.random() < 0.8 else _random_text(rng)
        assert split_ij(merge_ij(i, j)) == (i, j), (i, j)


def test_marker_lines_in_a_source_are_refused_not_mangled():
    for bad in ["x\n=======\ny\n", "<<<<<<< .i\n", "\\ No newline at end of file"]:
        try:
            merge_ij(bad, "x\n")
        except ValueError:
            continue
        raise AssertionError(f"accepted {bad!r}")


def test_unclosed_block_is_an_error():
    try:
        split_ij("<<<<<<< .i\nx\n=======\n")
    except ValueError:
        return
    raise AssertionError("accepted an unclosed block")


def test_pack_then_unpack_is_exact_fuzzed():
    rng = random.Random(42)
    for _ in range(500):
        files = {"i": ("t (1).i", _random_text(rng).encode("utf-8"))}
        if rng.random() < 0.7:
            files["j"] = ("t (1).j", _random_text(rng).encode("utf-8"))
            if rng.random() < 0.7:
                files["k"] = ("t (1).k", _random_text(rng).encode("utf-8"))
        assert unpack_ijk(pack_ijk(files)) == files


def test_ijk_reads_like_the_house_style():
    packed = pack_ijk({"i": ("a.i", b"Title\nbody\n"), "j": ("a.j", b"Title\nbody\n")})
    assert packed.decode().startswith("=" * 60 + "\ni: a.i (11 bytes)\n" + "=" * 60 + "\nTitle\n")


def test_damaged_ijk_is_an_error_not_a_guess():
    good = pack_ijk({"i": ("a.i", b"abc"), "j": ("a.j", b"abc")})
    damaged = [
        good[:-3],                                 # truncated
        good.replace(b"(3 bytes)", b"(9 bytes)", 1),  # wrong size
        good.replace(b"i: a.i", b"q: a.i"),        # unknown section
        pack_ijk({"i": ("a.i", b"x")})[: -1] + b"!",  # missing separator
    ]
    j_first = good[good.index(b"=" * 60 + b"\nj:"):] + good[:good.index(b"=" * 60 + b"\nj:")]
    damaged.append(j_first)                        # out of order
    for d in damaged:
        try:
            unpack_ijk(d)
        except ValueError:
            continue
        raise AssertionError(f"accepted {d!r}")


def test_cli_round_trip_through_files():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "x.i").write_bytes(b"Title\r\n-? Open?\r\n")
        (d / "x.j").write_bytes(b"Title\r\nClosed.\r\n")
        (d / "x.k").write_bytes(b'`title`body`text!("Title";"Closed.";"...")\n')
        assert ijk_files.main(["merge", str(d / "x.i"), str(d / "x.j")]) == 0
        assert ijk_files.main(["pack", str(d / "x.i"), str(d / "x.j"), str(d / "x.k")]) == 0
        out = d / "out"
        out.mkdir()
        ijk_files.main(["split", str(d / "x.ij"), "-d", str(out)])
        assert (out / "x.i").read_bytes() == (d / "x.i").read_bytes()
        assert (out / "x.j").read_bytes() == (d / "x.j").read_bytes()
        (out / "x.i").unlink(); (out / "x.j").unlink()
        ijk_files.main(["unpack", str(d / "x.ijk"), "-d", str(out)])
        for ext in "ijk":
            assert (out / f"x.{ext}").read_bytes() == (d / f"x.{ext}").read_bytes()


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
