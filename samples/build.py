"""
Rebuilds every sample output from src/. Run from anywhere:

    python3 samples/build.py [OUT_DIR]

For each NAME in src/: NAME.j is src/NAME.j if the author wrote one,
otherwise src/NAME.i promoted unchanged (only if it's ready). Then
NAME.k is compiled from NAME.j, NAME.ij merges NAME.i with NAME.j, and
NAME.ijk packs all three. A NAME.i that isn't ready gets nothing.
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

import ijk_files  # noqa: E402
import pipeline  # noqa: E402


def build(out: Path) -> list:
    out.mkdir(parents=True, exist_ok=True)
    report = []
    for i_path in sorted((HERE / "src").glob("*.i")):
        name = i_path.stem
        authored = HERE / "src" / f"{name}.j"
        ready = pipeline.run_pipeline(i_path)
        if not ready.ok and not authored.exists():
            report.append(ready.summary())
            continue
        j_bytes = authored.read_bytes() if authored.exists() else i_path.read_bytes()
        (out / f"{name}.j").write_bytes(j_bytes)
        result = pipeline.run_pipeline(out / f"{name}.j")
        if not result.ok:
            raise SystemExit(result.summary())
        k_bytes = result.k_source.encode("utf-8")
        (out / f"{name}.k").write_bytes(k_bytes)
        i_text, j_text = i_path.read_text(encoding="utf-8", newline=""), j_bytes.decode("utf-8")
        (out / f"{name}.ij").write_text(ijk_files.merge_ij(i_text, j_text), encoding="utf-8", newline="")
        (out / f"{name}.ijk").write_bytes(ijk_files.pack_ijk({
            "i": (f"{name}.i", i_path.read_bytes()),
            "j": (f"{name}.j", j_bytes),
            "k": (f"{name}.k", k_bytes),
        }))
        report.append(f"PASS  {name}: .j .k .ij .ijk")
    return report


if __name__ == "__main__":
    print("\n".join(build(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE)))
