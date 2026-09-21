from __future__ import annotations

import argparse
import json
import sys

from .audit import audit_file, audit_process
from .model import Report
from .parser import parse_file

VERSION = "1.0.0"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="env-doctor", description="Audit dotenv files and development environment configuration locally.")
    parser.add_argument("--version", action="version", version=f"Env Doctor {VERSION} — Radwan Abdulhadi Ahmed / @rad03i2")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Audit a dotenv file.")
    check.add_argument("path", help="Path to the dotenv file.")
    check.add_argument("--example", help="Optional .env.example contract to compare against.")
    check.add_argument("--json", action="store_true", dest="as_json", help="Print machine-readable JSON.")
    check.add_argument("--strict", action="store_true", help="Treat warnings as failures.")

    process = sub.add_parser("process", help="Audit the current process environment against an example file.")
    process.add_argument("--example", required=True, help="Path to the .env.example contract.")
    process.add_argument("--json", action="store_true", dest="as_json", help="Print machine-readable JSON.")
    process.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    return parser


def _render(report: Report) -> str:
    lines = [f"Env Doctor: {report.source}", f"Variables inspected: {report.variables}"]
    if not report.findings:
        lines.append("OK: no findings")
        return "\n".join(lines)
    for finding in report.findings:
        location = f" line {finding.line}" if finding.line is not None else ""
        key = f" [{finding.key}]" if finding.key else ""
        lines.append(f"{finding.severity.upper():7} {finding.code}{key}{location}: {finding.message}")
    lines.append(f"Summary: {report.errors} error(s), {report.warnings} warning(s)")
    return "\n".join(lines)


def _exit_code(report: Report, strict: bool) -> int:
    return 1 if report.errors or (strict and report.warnings) else 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "check":
            actual = parse_file(args.path)
            example = parse_file(args.example) if args.example else None
            report = audit_file(actual, args.path, example)
        else:
            example = parse_file(args.example)
            report = audit_process(example)
    except ValueError as exc:
        print(f"env-doctor: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(_render(report))
    return _exit_code(report, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
