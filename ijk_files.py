"""
.ij and .ijk files: more than one stage of the pipeline in one file.

    .ij   -- the merged result of a .i and a .j. Lines the two share
             appear once; where they differ, both versions appear in a
             marked block. Either file can be recovered exactly.
    .ijk  -- the .i, .j and .k together in one file, each under its
             own banner. Unpacks to the original bytes.

Both formats are lossless: split_ij(merge_ij(i, j)) == (i, j) and
unpack_ijk(pack_ijk(files)) == files, down to line endings.

Usage:
    python3 ijk_files.py merge  NAME.i NAME.j  [-o NAME.ij]
    python3 ijk_files.py split  NAME.ij        [-d DIR]
    python3 ijk_files.py pack   NAME.i [NAME.j [NAME.k]] [-o NAME.ijk]
    python3 ijk_files.py unpack NAME.ijk       [-d DIR]
    python3 ijk_files.py check  NAME.ijk       [--show]

check reads a .ijk as Judah defines it: "rosetta stones with the same
thing said three different ways ... a definition that can easily be
shown to be true or false given a review by a human." The k-to-j half
is mechanical: the k section, run in oK, must hold exactly the j
section's text. The j-to-i half is for a person: check counts where
they differ, and --show prints the .ij view of those places.
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

# --- .ij ------------------------------------------------------------------
#
# Merge markers are git's, labeled by file type, so any editor that
# highlights merge conflicts highlights these. A side whose last line
# has no newline gets git's own "\ No newline at end of file" line.

OPEN, MID, CLOSE = "<<<<<<< .i", "=======", ">>>>>>> .j"
NO_EOL = "\\ No newline at end of file"
_RESERVED = (OPEN, MID, CLOSE, NO_EOL)


_LINE = re.compile(r"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+$")


def _lines(text: str) -> list:
    # Not str.splitlines: that also breaks at form feed, \x1c-\x1e and
    # Unicode line separators, which are ordinary characters here.
    return _LINE.findall(text)


def _check_unreserved(text: str, name: str):
    for n, line in enumerate(_lines(text), start=1):
        if line.rstrip("\r\n") in _RESERVED:
            raise ValueError(f"{name} line {n} is a reserved .ij marker: {line.rstrip()!r}")


def _side(lines: list) -> list:
    """A block's lines, with the last one closed off if it had no newline."""
    if lines and not lines[-1].endswith(("\n", "\r")):
        return lines[:-1] + [lines[-1] + "\n", NO_EOL + "\n"]
    return lines


def merge_ij(i_text: str, j_text: str) -> str:
    _check_unreserved(i_text, ".i")
    _check_unreserved(j_text, ".j")
    i_lines, j_lines = _lines(i_text), _lines(j_text)
    out = []
    matcher = difflib.SequenceMatcher(None, i_lines, j_lines, autojunk=False)
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            out.extend(i_lines[i1:i2])
            continue
        if out and not out[-1].endswith(("\n", "\r")):
            # Only reachable if a shared region ends mid-line, which
            # line-based matching can't produce. Guard, not a feature.
            raise AssertionError("shared region ended without a newline")
        out.append(OPEN + "\n")
        out.extend(_side(i_lines[i1:i2]))
        out.append(MID + "\n")
        out.extend(_side(j_lines[j1:j2]))
        out.append(CLOSE + "\n")
    return "".join(out)


def split_ij(ij_text: str):
    """Recovers (i_text, j_text) from a .ij."""
    i_out, j_out = [], []
    mode = None  # None (shared), "i", or "j"
    for line in _lines(ij_text):
        bare = line.rstrip("\r\n")
        if bare == OPEN and mode is None:
            mode = "i"
        elif bare == MID and mode == "i":
            mode = "j"
        elif bare == CLOSE and mode == "j":
            mode = None
        elif bare == NO_EOL and mode in ("i", "j"):
            side = i_out if mode == "i" else j_out
            side[-1] = side[-1][:-1]  # drop the newline merge_ij added
        elif mode is None:
            i_out.append(line)
            j_out.append(line)
        else:
            (i_out if mode == "i" else j_out).append(line)
    if mode is not None:
        raise ValueError(f".ij ends inside an unclosed merge block (in the .{mode} side)")
    return "".join(i_out), "".join(j_out)


# --- .ijk -----------------------------------------------------------------
#
# Each section sits under a banner in the same shape as the house .i
# style (a line of "=" above and below). The banner carries the
# section's byte count, which is what unpacking trusts -- a real file
# can contain "====" lines of its own, so the banners can't be found by
# searching for them. One newline follows each section's bytes so the
# next banner always starts on its own line.

RULE = "=" * 60
_BANNER = re.compile(rb"([ijk]): (.+) \((\d+) bytes\)")
ORDER = ("i", "j", "k")


def pack_ijk(files: dict) -> bytes:
    """files maps "i"/"j"/"k" to (name, bytes). At least "i" is needed."""
    if "i" not in files or set(files) - set(ORDER):
        raise ValueError(".ijk takes an i section and optionally j and k")
    out = bytearray()
    for kind in ORDER:
        if kind not in files:
            continue
        name, data = files[kind]
        out += f"{RULE}\n{kind}: {name} ({len(data)} bytes)\n{RULE}\n".encode("utf-8")
        out += data + b"\n"
    return bytes(out)


def unpack_ijk(data: bytes) -> dict:
    """Returns {"i"/"j"/"k": (name, bytes)} exactly as packed."""
    rule = RULE.encode() + b"\n"
    files, pos, seen = {}, 0, []
    while pos < len(data):
        if not data.startswith(rule, pos):
            raise ValueError(f"expected a banner at byte {pos}")
        line_end = data.index(b"\n", pos + len(rule))
        match = _BANNER.fullmatch(data[pos + len(rule):line_end])
        if not match or not data.startswith(rule, line_end + 1):
            raise ValueError(f"malformed banner at byte {pos}")
        kind, name, size = match.group(1).decode(), match.group(2).decode("utf-8"), int(match.group(3))
        start = line_end + 1 + len(rule)
        body = data[start:start + size]
        if len(body) != size or data[start + size:start + size + 1] != b"\n":
            raise ValueError(f"section {kind} ({name}) is shorter than its banner says")
        if kind in files or (seen and ORDER.index(kind) < ORDER.index(seen[-1])):
            raise ValueError(f"section {kind} is repeated or out of order")
        files[kind] = (name, body)
        seen.append(kind)
        pos = start + size + 1
    if "i" not in files:
        raise ValueError(".ijk has no i section")
    return files


# --- Rosetta check -------------------------------------------------------

def check_ijk(data: bytes) -> dict:
    """
    Returns {"k_matches_j": True/False/None, "i_j_differences": int or
    None, "ij": the .ij text or None}. None means the sections needed
    for that half aren't there.
    """
    import pipeline  # imported here so .ij/.ijk work without oK installed

    sections = unpack_ijk(data)
    report = {"k_matches_j": None, "i_j_differences": None, "ij": None}
    if "j" in sections and "k" in sections:
        j_text = sections["j"][1].decode("utf-8")
        k_source = sections["k"][1].decode("utf-8")
        # All three fields, as the pipeline checks them: text must be the
        # j exactly, and title/body must be the view of it, so an edit to
        # the k's body alone can't pass.
        run = pipeline._ok.run_k_file(
            f"d:{k_source},/{{(#x;+/x;+/(1+!#x)*x)}}'0+'(d`title;d`body;d`text)")
        title, body = pipeline._expected_title_body(j_text)
        expected = [str(n) for field in (title, body, j_text) for n in pipeline._fingerprint(field)]
        report["k_matches_j"] = run.ok and run.stdout.split() == expected
    if "i" in sections and "j" in sections:
        i_text = sections["i"][1].decode("utf-8")
        j_text = sections["j"][1].decode("utf-8")
        ij = merge_ij(i_text, j_text)
        report["i_j_differences"] = sum(1 for l in _lines(ij) if l.rstrip("\r\n") == OPEN)
        report["ij"] = ij
    return report


# --- CLI ------------------------------------------------------------------

def _read(path) -> str:
    return Path(path).read_text(encoding="utf-8", newline="")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Make and take apart .ij and .ijk files.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge"); m.add_argument("i"); m.add_argument("j"); m.add_argument("-o")
    s = sub.add_parser("split"); s.add_argument("ij"); s.add_argument("-d", default=".")
    p = sub.add_parser("pack"); p.add_argument("files", nargs="+"); p.add_argument("-o")
    u = sub.add_parser("unpack"); u.add_argument("ijk"); u.add_argument("-d", default=".")
    c = sub.add_parser("check"); c.add_argument("ijk"); c.add_argument("--show", action="store_true")
    args = parser.parse_args(argv)

    if args.cmd == "merge":
        out = Path(args.o or Path(args.i).with_suffix(".ij"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(merge_ij(_read(args.i), _read(args.j)), encoding="utf-8", newline="")
        print(f"wrote {out}")
    elif args.cmd == "split":
        src = Path(args.ij)
        i_text, j_text = split_ij(_read(src))
        Path(args.d).mkdir(parents=True, exist_ok=True)
        for suffix, text in ((".i", i_text), (".j", j_text)):
            dest = Path(args.d) / (src.stem + suffix)
            dest.write_text(text, encoding="utf-8", newline="")
            print(f"wrote {dest}")
    elif args.cmd == "pack":
        files = {}
        for f in map(Path, args.files):
            kind = f.suffix.lstrip(".")
            if kind not in ORDER or kind in files:
                parser.error(f"{f.name}: pack takes one each of .i, .j, .k")
            files[kind] = (f.name, f.read_bytes())
        out = Path(args.o or Path(args.files[0]).with_suffix(".ijk"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(pack_ijk(files))
        print(f"wrote {out}")
    elif args.cmd == "unpack":
        Path(args.d).mkdir(parents=True, exist_ok=True)
        for kind, (name, data) in unpack_ijk(Path(args.ijk).read_bytes()).items():
            dest = Path(args.d) / Path(name).name
            dest.write_bytes(data)
            print(f"wrote {dest}")
    elif args.cmd == "check":
        r = check_ijk(Path(args.ijk).read_bytes())
        k = {True: "yes, exactly", False: "NO", None: "can't tell (needs j and k)"}[r["k_matches_j"]]
        print(f"k says what j says: {k}")
        n = r["i_j_differences"]
        if n is None:
            print("j against i: can't tell (needs i and j)")
        elif n == 0:
            print("j against i: identical")
        else:
            print(f"j against i: {n} place(s) differ -- a person decides if they say the same thing")
            if args.show:
                print(r["ij"], end="")
        return 0 if r["k_matches_j"] is not False else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
