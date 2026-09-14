"""
Stage 1 of the ijk pipeline: .i -> .j.

This is the mechanical version of something this project has already
done by hand several times -- confirming an .i file's content and
renaming it .j (for example, notes.i -> notes.j).
Formalized here as an actual, testable transform rather than a manual
judgment call each time.

Rule Zero-equivalent for this stage: this code only ever *detects*
whether a file is ready. It never resolves a blocking marker's
content itself, never authors CONDITION-style field content, and
never renames a file on its own authority -- promotion requires the
caller (a human, or an explicit confirmed instruction) to act on the
report. Same discipline as everywhere else in this system: don't
guess silently, don't invent the resolution.
"""

from dataclasses import dataclass
from pathlib import Path

from markers import find_blocking_lines


@dataclass
class ReadinessReport:
    path: Path
    ready: bool
    blocking: list  # list of (line_number, marker, line_text)

    def summary(self) -> str:
        if self.ready:
            return f"{self.path.name}: ready -- no blocking markers found."
        lines = "\n".join(
            f"  line {n}: [{marker}] {text.strip()}"
            for n, marker, text in self.blocking
        )
        return (
            f"{self.path.name}: NOT ready -- "
            f"{len(self.blocking)} blocking marker(s):\n{lines}"
        )


def check_readiness(i_file_path: str) -> ReadinessReport:
    """
    Reads a .i file and reports whether it's ready to become .j --
    i.e., whether it contains zero blocking markers ("---" / "(...)"
    / bare "?"). Does not write anything. Does not rename anything.
    """
    path = Path(i_file_path)
    text = path.read_text(encoding="utf-8")
    blocking = find_blocking_lines(text)
    return ReadinessReport(path=path, ready=not blocking, blocking=blocking)


def promote(i_file_path: str, j_file_path: str) -> ReadinessReport:
    """
    Attempts the actual .i -> .j promotion. Refuses if the file isn't
    ready -- raises rather than silently writing a .j file that still
    has open questions baked into it. Copies content unchanged; this
    stage checks readiness, it doesn't edit prose.
    """
    report = check_readiness(i_file_path)
    if not report.ready:
        raise ValueError(
            "Refusing to promote -- file is not ready:\n" + report.summary()
        )
    Path(j_file_path).write_text(report.path.read_text(encoding="utf-8"), encoding="utf-8")
    return report
