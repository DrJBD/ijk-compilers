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
    out = _js(page, "var e=loadFeed(FEED); out={r:rows(e), t:[0,1,2].map(i=>docText(e,i))};")
    assert [(r["name"], r["title"]) for r in out["r"]] == [
        ("escapes", "Escapes"), ("hello", "Hello, oK"), ("revised", "Revised")]
    for name, text in zip(["escapes", "hello", "revised"], out["t"]):
        assert text == (ROOT / "samples" / f"{name}.j").read_text(encoding="utf-8", newline=""), name


def test_queries_run_and_errors_come_back_as_messages():
    page = _page(ROOT / "samples", "--prelude", ROOT / "candidate_ops.k")
    out = _js(page, "var e=loadFeed(FEED); out=[evaluate(e,'find[\"oK\"]'), evaluate(e,'1 2+1 2 3')];")
    assert out[0] == {"ok": True, "out": ',"hello"'}
    assert out[1] == {"ok": False, "out": "length error."}


def test_page_cannot_be_broken_out_of_by_document_text():
    d = Path(tempfile.mkdtemp())
    (d / "x.j").write_text('Title\n</script><script>alert(1)</script> "q" \\n\n', encoding="utf-8")
    page = _page(d)
    assert page.read_text(encoding="utf-8").count("</script>") == 3  # oK, core, UI -- nothing else
    out = _js(page, "var e=loadFeed(FEED); out=docText(e,0);")
    assert out == (d / "x.j").read_text(encoding="utf-8")


def test_the_i_side_never_reaches_a_page():
    d = Path(tempfile.mkdtemp())
    (d / "a.i").write_text("A\nsecret draft\n", encoding="utf-8")
    (d / "b.j").write_text("B\nconfirmed\n", encoding="utf-8")
    page = _page(d)
    assert "secret draft" not in page.read_text(encoding="utf-8")


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
