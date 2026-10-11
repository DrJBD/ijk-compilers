"""
Runs every test file in the repo and reports one line each.

    python3 run_tests.py

Each test file runs on its own, from its own directory, the way it was
written to. A file that fails has its full output printed. Exits 0 only
if every file passes.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

TESTS = [
    "stage1_i_to_j/test_transform.py",
    "stage2_j_to_k/test_transform.py",
    "stage2_j_to_k/test_validators.py",
    "oK_verification/test_run_ok_test.py",
    "test_pipeline.py",
    "test_ijk_files.py",
    "test_feed.py",
    "viewer/test_viewer.py",
    "test_examples.py",
]


def main() -> int:
    found = sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("**/test_*.py")
                   if "play" not in p.parts and "build" not in p.parts)
    missing = sorted(set(found) - set(TESTS))
    if missing:
        print("not in run_tests.py's list, add them: " + ", ".join(missing))
        return 1
    failed = []
    for name in TESTS:
        path = ROOT / name
        run = subprocess.run(
            [sys.executable, path.name], cwd=path.parent,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        lines = run.stdout.strip().splitlines()
        tally = lines[-1] if lines else "(no output)"
        print(f"{'PASS' if run.returncode == 0 else 'FAIL'}  {name:40} {tally}")
        if run.returncode != 0:
            failed.append((name, run.stdout))
    for name, output in failed:
        print(f"\n--- {name} ---\n{output}")
    print(f"\n{len(TESTS) - len(failed)}/{len(TESTS)} test files passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
