"""
Runs every command in EXAMPLES.md and checks its output against the page.

A ```console block holds "$ command" lines, each followed by the output it
prints (stdout and stderr together). Blocks run in order, in a scratch
copy of the repo, so the page's own build/ never touches the real one.
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
_BLOCK = re.compile(r"^```console\n(.*?)^```", re.S | re.M)


def steps(page: str) -> list:
    """[(command, expected output)] for every console block, in order."""
    found = []
    for block in _BLOCK.findall(page):
        for chunk in re.split(r"^\$ ", block, flags=re.M)[1:]:
            command, _, output = chunk.partition("\n")
            found.append((command, output))
    return found


def run_all(page: str) -> list:
    """Every step whose output differs: [(command, expected, got)]."""
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "build", "play", "__pycache__"))
        for command, expected in steps(page):
            got = subprocess.run(
                ["bash", "-c", command], cwd=repo, capture_output=False,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            ).stdout
            if got != expected:
                failures.append((command, expected, got))
    return failures


def test_page_has_examples():
    assert len(steps((ROOT / "EXAMPLES.md").read_text(encoding="utf-8"))) >= 10


def test_every_example_prints_what_the_page_says():
    failures = run_all((ROOT / "EXAMPLES.md").read_text(encoding="utf-8"))
    for command, expected, got in failures:
        print(f"$ {command}\n--- page says:\n{expected}--- got:\n{got}")
    assert not failures


def test_a_wrong_page_is_caught():
    page = "```console\n$ echo hello\ngoodbye\n```\n"
    assert len(run_all(page)) == 1


if __name__ == "__main__":
    import sys
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    passed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {name}  {e}")
    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(0 if passed == len(tests) else 1)
