"""
Tests for the viewer: builds a page from the samples and runs its own
script blocks in Node (oK plus the viewer's core), no browser needed.
Run from the repo root: python3 viewer/test_viewer.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_viewer  # noqa: E402

_NODE = r"""
const fs=require("fs"), vm=require("vm");
const html=fs.readFileSync(process.argv[1],"utf8");
const s=[...html.matchAll(/<script(?: id="viewer-core")?>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const c={}; vm.createContext(c); vm.runInContext(s[0],c); vm.runInContext(s[1],c);
vm.runInContext(process.argv[2],c); console.log(JSON.stringify(c.out));
"""


def _page(*args) -> Path:
    out = Path(tempfile.mkdtemp()) / "v.html"
    assert build_viewer.main([*map(str, args), "-o", str(out)]) == 0
    return out


def _js(page: Path, code: str):
    p = subprocess.run(["node", "-e", _NODE, str(page), code], capture_output=True, text=True, timeout=30)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


def test_lists_documents_and_shows_exact_text():
    page = _page(ROOT / "samples")
    out = _js(page, "var v=viewer, e=v.loadFeed(v.FEED); out={r:v.rows(e), t:[0,1,2].map(i=>v.docText(e,i))};")
    assert [(r["name"], r["title"]) for r in out["r"]] == [
        ("escapes", "Escapes"), ("hello", "Hello, oK"), ("revised", "Revised")]
    for name, text in zip(["escapes", "hello", "revised"], out["t"]):
        assert text == (ROOT / "samples" / f"{name}.j").read_text(encoding="utf-8", newline=""), name


def test_queries_run_and_errors_come_back_as_messages():
    page = _page(ROOT / "samples", "--prelude", ROOT / "candidate_ops.k")
    out = _js(page, "var v=viewer, e=v.loadFeed(v.FEED); out=[v.evaluate(e,'find[\"oK\"]'), v.evaluate(e,'1 2+1 2 3')];")
    assert out[0] == {"ok": True, "out": ',"hello"'}
    assert out[1] == {"ok": False, "out": "length error."}


def test_page_cannot_be_broken_out_of_by_document_text():
    d = Path(tempfile.mkdtemp())
    (d / "x.j").write_text('Title\n</script><script>alert(1)</script> "q" \\n\n', encoding="utf-8")
    page = _page(d)
    assert page.read_text(encoding="utf-8").count("</script>") == 3  # oK, core, UI -- nothing else
    out = _js(page, "var v=viewer, e=v.loadFeed(v.FEED); out=v.docText(e,0);")
    assert out == (d / "x.j").read_text(encoding="utf-8")


def test_the_i_side_never_reaches_a_page():
    d = Path(tempfile.mkdtemp())
    (d / "a.i").write_text("A\nsecret draft\n", encoding="utf-8")
    (d / "b.j").write_text("B\nconfirmed\n", encoding="utf-8")
    page = _page(d)
    assert "secret draft" not in page.read_text(encoding="utf-8")


# Awkward patterns: CR, CRLF, backslash before n, quotes, one character,
# non-ASCII, an emoji, mixed case.
PATTERNS = ["oK", "OK", "a", '"', "\\", "\\n", "\r", "\r\n", "\u2014", "\U0001F600", "zz", "Line", "end."]
EDGE = {
    "a": 'Alpha\nA "quoted" Line with \\n written out\nend.',
    "b": "Beta\r\nwindows line\r\n\u2014 dash \U0001F600\r\n",
    "c": "Gamma",
    "d": "I am not god.\nI am not God.\nGOD",
    "e": "",
}


def _edge_page():
    d = Path(tempfile.mkdtemp())
    for name, text in EDGE.items():
        (d / f"{name}.j").write_text(text, encoding="utf-8", newline="")
    return _page(d)


def test_rosetta_badge_agrees_differs_and_says_when_it_cant_tell():
    page = _page(ROOT / "samples")
    out = _js(page, "var v=viewer, e=v.loadFeed(v.FEED); var a=[0,1,2].map(i=>v.rosetta(e,i));"
                    "v.JTEXT[1]=v.JTEXT[1].replace('ask','say'); var b=v.rosetta(e,1);"
                    "v.JTEXT[2]=null; out=[a,b,v.rosetta(e,2)];")
    assert out == [[True, True, True], False, None]
    # a .k with no .j beside it has nothing to compare against
    d = Path(tempfile.mkdtemp())
    (d / "lone.k").write_bytes((ROOT / "samples" / "hello.k").read_bytes())
    assert _js(_page(d), "var v=viewer, e=v.loadFeed(v.FEED); out=v.rosetta(e,0);") is None


def test_page_escapes_k_strings_exactly_as_stage_2_does():
    k_string = __import__("feed")._k_string
    samples = PATTERNS + ["", "x", "\r", "a\\nb", "\\\\", 'q"\r\\']
    out = _js(_page(ROOT / "samples"), "out=" + json.dumps(samples) + ".map(s=>viewer.kString(s));")
    assert out == [k_string(s) for s in samples]


def test_find_matches_python_with_and_without_case():
    texts = list(EDGE.values())
    pats = PATTERNS + ["god", "God", "GOD"]
    for match_case in (False, True):
        out = _js(_edge_page(), "var v=viewer, e=v.loadFeed(v.FEED); out="
                  + json.dumps(pats) + f".map(p=>v.find(e,p,{str(match_case).lower()}));")
        for p, got in zip(pats, out):
            norm = (lambda s: s) if match_case else str.lower
            hits = [int(norm(p) in norm(t)) for t in texts]
            lines = [sum(norm(p) in norm(l) for l in t.split("\n")) for t in texts]
            assert got == {"hits": hits, "lines": lines}, (p, match_case, got)
    assert _js(_edge_page(), "out=viewer.find(viewer.loadFeed(viewer.FEED),'',true);") is None


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
