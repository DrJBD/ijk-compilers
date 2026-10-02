"""
The whole ijk pipeline, end to end: .i -> .j -> .k -> oK.

Each stage already has its own tests. This runs a file through all of
them in order and reports how far it got:

    1. readiness   -- stage 1's marker check. A file with blocking
                      markers stops here; nothing downstream runs.
    2. compile     -- stage 2's .j -> .k transform.
    3. validate    -- stage 2's .k validators (currently ok -> oK).
    4. evaluate    -- the .k source runs cleanly in the real oK
                      interpreter.
    5. round-trip  -- inside oK, the dict's `text` matches the source
                      file exactly (length, sum and position-weighted
                      sum of its characters, computed separately in
                      oK and in Python), and `title`/`body` match
                      under K's own `~`.

Writes nothing by default. Stage 1's rule holds here too: the
pipeline reports on a .i file, it never renames it or resolves its
markers. With --out DIR, the .j and .k produced for ready files are
written into DIR; the source file is never touched.

Usage:
    python3 pipeline.py FILE_OR_DIR [...] [--out DIR]

A directory is searched (not recursively) for *.i and *.j files. A .j
file skips the readiness check -- it has already been promoted.
"""

import argparse
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).parent


def _load(name: str, path: Path):
    # Both stages name their module transform.py, so each is loaded
    # from its own path under its own name instead of via sys.path.
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(_ROOT / "stage1_i_to_j"))  # stage 1 imports markers
_stage1 = _load("stage1_transform", _ROOT / "stage1_i_to_j" / "transform.py")
_stage2 = _load("stage2_transform", _ROOT / "stage2_j_to_k" / "transform.py")
_validators = _load("stage2_validators", _ROOT / "stage2_j_to_k" / "validators.py")
_ok = _load("run_ok_test", _ROOT / "oK_verification" / "run_ok_test.py")

STAGES = ["readiness", "compile", "validate", "evaluate", "round-trip"]


@dataclass
class PipelineResult:
    path: Path
    passed: list = field(default_factory=list)  # stage names, in order
    failed_at: str = None  # first stage that failed, or None
    detail: str = ""
    k_source: str = None

    @property
    def ok(self) -> bool:
        return self.failed_at is None

    def summary(self) -> str:
        if self.ok:
            return f"PASS  {self.path.name}"
        text = f"FAIL  {self.path.name} -- stopped at {self.failed_at}"
        if self.detail:
            text += "\n" + "\n".join("      " + l for l in self.detail.splitlines())
        return text


def _expected_title_body(text: str):
    # Mirrors stage 2's own split, so the view fields compare like with
    # like: first line is the title, the rest (stripped) is the body.
    lines = text.splitlines()
    title = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip()
    return title, body


def _fingerprint(text: str):
    # oK holds a string as UTF-16 code units (an emoji is two), so the
    # check counts the same way: length, sum, and position-weighted sum.
    # Computed here in Python and separately inside oK, so a stage 2
    # escaping bug can't make both sides agree.
    units = text.encode("utf-16-le")
    codes = [int.from_bytes(units[i:i + 2], "little") for i in range(0, len(units), 2)]
    return (len(codes), sum(codes), sum((i + 1) * c for i, c in enumerate(codes)))


def run_pipeline(path) -> PipelineResult:
    path = Path(path)
    result = PipelineResult(path=path)

    if path.suffix == ".i":
        report = _stage1.check_readiness(str(path))
        if not report.ready:
            result.failed_at = "readiness"
            result.detail = report.summary()
            return result
    result.passed.append("readiness")

    k_source = _stage2.j_to_k(str(path))
    result.k_source = k_source
    result.passed.append("compile")

    issues = _validators.validate(k_source)
    if issues:
        result.failed_at = "validate"
        result.detail = "\n".join(str(i) for i in issues)
        return result
    result.passed.append("validate")

    evaluated = _ok.run_k(f"d:{k_source}d[`title]")
    if not evaluated.ok:
        result.failed_at = "evaluate"
        result.detail = evaluated.stdout.strip()
        return result
    result.passed.append("evaluate")

    source = path.read_text(encoding="utf-8", newline="")
    title, body = _expected_title_body(source)
    k_string = _stage2.k_string
    check = _ok.run_k(
        f"d:{k_source}t:0+d[`text]\n"
        f"(d[`title]~{k_string(title)};d[`body]~{k_string(body)})\n"
        f"(#t;+/t;+/(1+!#t)*t)"
    )
    lines = check.stdout.strip().splitlines()
    expected = " ".join(str(n) for n in _fingerprint(source))
    if not check.ok or lines[-2].strip() != "1 1" or lines[-1].strip() != expected:
        result.failed_at = "round-trip"
        result.detail = (
            "oK reported (title match; body match), then text (length sum weighted):\n"
            + "\n".join(lines[-2:])
            + f"\nexpected text fingerprint: {expected}"
        )
        return result
    result.passed.append("round-trip")

    return result


def collect(targets) -> list:
    files = []
    for t in targets:
        p = Path(t).expanduser()
        if p.is_dir():
            files.extend(sorted(f for f in p.iterdir() if f.suffix in (".i", ".j")))
        else:
            files.append(p)
    return files


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run .i/.j files through i -> j -> k -> oK.")
    parser.add_argument("targets", nargs="+", help=".i/.j files or directories")
    parser.add_argument("--out", help="write the .j and .k for files that pass into this directory")
    args = parser.parse_args(argv)

    files = collect(args.targets)
    if not files:
        print("no .i or .j files found")
        return 1

    out = Path(args.out).expanduser() if args.out else None
    if out:
        out.mkdir(parents=True, exist_ok=True)

    results = [run_pipeline(f) for f in files]
    for r in results:
        print(r.summary())
        if out and r.ok:
            stem = r.path.stem
            (out / f"{stem}.j").write_bytes(r.path.read_bytes())
            (out / f"{stem}.k").write_text(r.k_source, encoding="utf-8")

    passed = sum(r.ok for r in results)
    print(f"\n{passed}/{len(results)} through to oK")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
