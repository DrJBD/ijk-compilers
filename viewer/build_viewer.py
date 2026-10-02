"""
Builds a local context viewer: one HTML file holding oK and a feed, for
browsing a context and querying it in K, offline.

    python3 viewer/build_viewer.py FILE_OR_DIR [...] [--prelude FILE] [-o viewer.html]

The feed is made by feed.py, so its rules hold: the .i side never goes
in. oK.js is read from the clone next to OK_REPL (default ~/code/ok)
and inlined with its MIT notice. Nothing is fetched when the page
opens, so it works with no network.

The page lists each document's name and title. Clicking one shows its
text, and the box at the bottom runs K against the same environment,
where docs, corpus and any prelude definitions are already loaded.
"""

import argparse
import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import feed  # noqa: E402

_OK_DIR = Path(os.environ.get("OK_REPL", Path.home() / "code" / "ok" / "repl.js")).expanduser().parent


def _script_safe(text: str) -> str:
    # Inside <script>, only "</" can end the element early.
    return text.replace("</", "<\\/")


def build_html(feed_text: str, title: str) -> str:
    ok_js = (_OK_DIR / "oK.js").read_text(encoding="utf-8")
    licence = (_OK_DIR / "LICENSE.txt").read_text(encoding="utf-8")
    page = (Path(__file__).parent / "viewer.html.in").read_text(encoding="utf-8")
    return (
        page.replace("@@TITLE@@", html.escape(title))
        .replace("@@OK_LICENSE@@", _script_safe(licence.replace("*/", "* /")))
        .replace("@@OK_JS@@", _script_safe(ok_js))
        .replace("@@FEED@@", _script_safe(json.dumps(feed_text)))
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build an offline oK viewer for a context.")
    parser.add_argument("targets", nargs="+")
    parser.add_argument("--prelude", action="append", default=[])
    parser.add_argument("-o", default="viewer.html")
    parser.add_argument("--title", default="ijk context")
    args = parser.parse_args(argv)

    skipped = []
    files = feed.collect(args.targets, skipped)
    for s in skipped:
        print(f"skipped {s.name}: the .i side never goes in a corpus", file=sys.stderr)
    if not files:
        print("no ijk files found", file=sys.stderr)
        return 1
    try:
        text = feed.build_feed(files)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    for prelude in args.prelude:
        text += Path(prelude).read_text(encoding="utf-8").rstrip("\n") + "\n"

    Path(args.o).write_text(build_html(text, args.title), encoding="utf-8")
    print(f"wrote {args.o} ({len(files)} document(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
