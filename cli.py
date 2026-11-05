"""Command-line interface: `whyfail [pytest arguments]`."""

from __future__ import annotations

import os
import sys
from typing import List, Optional

from . import __version__
from .runner import Report, run_pytest


class Style:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.enabled else text

    def red(self, t): return self._wrap("1;31", t)
    def green(self, t): return self._wrap("1;32", t)
    def yellow(self, t): return self._wrap("33", t)
    def cyan(self, t): return self._wrap("36", t)
    def bold(self, t): return self._wrap("1", t)
    def dim(self, t): return self._wrap("2", t)


def render(report: Report, style: Style) -> str:
    lines: List[str] = [""]

    if not report.failures and report.returncode == 0:
        lines.append(style.green(f"✓ All {report.passed} tests pass. Nothing to explain."))
        return "\n".join(lines) + "\n"

    if "No module named pytest" in report.raw_output:
        lines.append(style.yellow("pytest is not installed in this environment."))
        lines.append("Install it with: pip install pytest")
        return "\n".join(lines) + "\n"

    if not report.failures:
        # Pytest failed for a reason we do not parse (collection error, config...).
        lines.append(style.yellow("whyfail could not parse these failures. Raw pytest output:"))
        lines.append(report.raw_output)
        return "\n".join(lines) + "\n"

    for index, failure in enumerate(report.failures, start=1):
        exp = failure.explanation
        lines.append(style.red(f"✗ {failure.test}"))
        lines.append(f"  {style.bold(exp.title)}")
        lines.append(f"  {style.dim('Why:')} {exp.why}")
        lines.append(f"  {style.cyan('Fix:')} {exp.fix}")
        if index < len(report.failures):
            lines.append("")

    lines.append("")
    summary = f"{len(report.failures)} failure(s) explained"
    if report.passed:
        summary += f", {report.passed} passed"
    lines.append(style.bold(summary))
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if args and args[0] in ("-V", "--version"):
        print(f"whyfail {__version__}")
        return 0

    color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    style = Style(enabled=color)

    try:
        report = run_pytest(args)
    except FileNotFoundError:
        print("error: Python could not start pytest. Install it with: pip install pytest", file=sys.stderr)
        return 2

    sys.stdout.write(render(report, style))
    return 0 if report.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
