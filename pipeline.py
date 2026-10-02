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
    5. round-trip  -- inside oK, the dict's title and body match the
                      source file's exactly (K's own `~`, not a
                      Python-side string compare).

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
    # Mirrors stage 2's own split, so the round-trip compares like with
    # like: first line is the title, the rest (stripped) is the body.
    lines = text.splitlines()
    title = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip()
    return title, body


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

    title, body = _expected_title_body(path.read_text(encoding="utf-8"))
    esc = _stage2.escape_k_string
    check = _ok.run_k(
        f'd:{k_source}(d[`title]~"{esc(title)}";d[`body]~"{esc(body)}")'
    )
    if not check.ok or "1 1" not in check.stdout:
        result.failed_at = "round-trip"
        result.detail = "oK reported (title match; body match):\n" + check.stdout.strip()
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
            (out / f"{stem}.j").write_text(r.path.read_text(encoding="utf-8"), encoding="utf-8")
            (out / f"{stem}.k").write_text(r.k_source, encoding="utf-8")

    passed = sum(r.ok for r in results)
    print(f"\n{passed}/{len(results)} through to oK")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
