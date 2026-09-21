from __future__ import annotations

import os
import re
from collections.abc import Mapping

from .model import Finding, Report
from .parser import ParsedEnv

_PLACEHOLDERS = {
    "changeme", "change-me", "change_me", "replace-me", "replace_me", "example",
    "placeholder", "your-value", "your_value", "todo", "xxx", "secret", "password",
}
_SENSITIVE_NAME = re.compile(r"(?:SECRET|TOKEN|PASSWORD|PASSWD|API_?KEY|PRIVATE_?KEY|ACCESS_?KEY)", re.I)


def _value_findings(parsed: ParsedEnv, *, example: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    for key, value in parsed.values.items():
        line = parsed.lines.get(key)
        normalized = value.strip().lower()
        if not value.strip():
            severity = "warning" if example else "error"
            findings.append(Finding("empty-value", severity, f"Variable {key} has an empty value.", key=key, line=line))
        elif normalized in _PLACEHOLDERS or normalized.startswith(("your-", "your_", "replace-", "replace_")):
            findings.append(Finding("placeholder-value", "warning", f"Variable {key} appears to contain a placeholder.", key=key, line=line))
        if example and _SENSITIVE_NAME.search(key) and value.strip() and normalized not in _PLACEHOLDERS and not normalized.startswith(("your-", "your_", "replace-", "replace_")):
            findings.append(Finding("example-secret-risk", "warning", f"Sensitive-looking variable {key} has a concrete value in the example file.", key=key, line=line))
    return findings


def audit_file(actual: ParsedEnv, source: str, example: ParsedEnv | None = None) -> Report:
    report = Report(source=source, variables=len(actual.values))
    report.findings.extend(actual.findings)
    report.findings.extend(_value_findings(actual))
    if example is not None:
        report.findings.extend(example.findings)
        report.findings.extend(_value_findings(example, example=True))
        expected = set(example.values)
        present = set(actual.values)
        for key in sorted(expected - present):
            report.findings.append(Finding("missing-variable", "error", f"Required variable {key} is missing.", key=key))
        for key in sorted(present - expected):
            report.findings.append(Finding("unexpected-variable", "warning", f"Variable {key} is not documented in the example file.", key=key, line=actual.lines.get(key)))
    return report


def audit_process(example: ParsedEnv, environ: Mapping[str, str] | None = None) -> Report:
    environment = os.environ if environ is None else environ
    report = Report(source="process", variables=len(environment))
    report.findings.extend(example.findings)
    report.findings.extend(_value_findings(example, example=True))
    for key in sorted(example.values):
        if key not in environment:
            report.findings.append(Finding("missing-variable", "error", f"Required variable {key} is missing from the process environment.", key=key))
        elif not environment[key].strip():
            report.findings.append(Finding("empty-value", "error", f"Process variable {key} is empty.", key=key))
    return report
