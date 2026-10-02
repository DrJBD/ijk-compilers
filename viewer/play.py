"""
Rebuild the viewer from the play folder and open it.

    python3 viewer/play.py            build play/viewer.html and open it
    python3 viewer/play.py --watch    also rebuild whenever a file changes

play/ is gitignored: nothing written there is committed. Write .j files
(or .k / .ijk). A .i is skipped, as everywhere else: the .i side never
goes in a corpus. candidate_ops.k is loaded, so find, byname and the
rest work in the query box.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_viewer  # noqa: E402

PLAY = ROOT / "play"
OUT = PLAY / "viewer.html"


def build() -> bool:
    if not any(f.suffix in (".j", ".k", ".ijk") for f in PLAY.iterdir()):
        print("play/ has no .j yet. Write one there (first line is the title).")
        return False
    return build_viewer.main([str(PLAY), "--prelude", str(ROOT / "candidate_ops.k"),
                              "-o", str(OUT), "--title", "ijk play"]) == 0


def snapshot():
    return {f: f.stat().st_mtime for f in PLAY.iterdir() if f.suffix in (".i", ".j", ".k", ".ijk")}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build and open the play viewer.")
    parser.add_argument("--watch", action="store_true", help="rebuild on every save")
    args = parser.parse_args(argv)
    PLAY.mkdir(exist_ok=True)
    built = build()
    if built:
        subprocess.run(["open", str(OUT)])
    if not args.watch:
        return 0 if built else 1
    print("watching play/ -- save a file, then refresh the page. Ctrl-C to stop.")
    seen = snapshot()
    try:
        while True:
            time.sleep(1)
            now = snapshot()
            if now != seen:
                seen = now
                if build() and not built:
                    built = True
                    subprocess.run(["open", str(OUT)])
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
