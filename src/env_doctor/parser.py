from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .model import Finding

_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass
class ParsedEnv:
    values: dict[str, str] = field(default_factory=dict)
    lines: dict[str, int] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)


def _strip_inline_comment(value: str) -> str:
    if not value or value[0] in "\"'":
        return value
    marker = re.search(r"\s+#", value)
    return value[: marker.start()].rstrip() if marker else value.strip()


def _decode_value(raw: str, line_no: int, findings: list[Finding]) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if raw[0] not in "\"'":
        return _strip_inline_comment(raw)
    quote = raw[0]
    escaped = False
    end = None
    for index in range(1, len(raw)):
        char = raw[index]
        if quote == '"' and char == "\\" and not escaped:
            escaped = True
            continue
        if char == quote and not escaped:
            end = index
            break
        escaped = False
    if end is None:
        findings.append(Finding("unclosed-quote", "error", "Quoted value is not closed.", line=line_no))
        return raw[1:]
    tail = raw[end + 1 :].strip()
    if tail and not tail.startswith("#"):
        findings.append(Finding("trailing-content", "warning", "Unexpected content follows a quoted value.", line=line_no))
    value = raw[1:end]
    if quote == '"':
        value = value.replace(r"\n", "\n").replace(r"\r", "\r").replace(r"\t", "\t").replace(r'\"', '"').replace(r"\\", "\\")
    return value


def parse_text(text: str) -> ParsedEnv:
    result = ParsedEnv()
    for line_no, original in enumerate(text.splitlines(), 1):
        stripped = original.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[7:].lstrip()
        if "=" not in stripped:
            result.findings.append(Finding("malformed-line", "error", "Expected KEY=VALUE syntax.", line=line_no))
            continue
        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        if not _KEY.fullmatch(key):
            result.findings.append(Finding("invalid-name", "error", "Invalid environment variable name.", key=key or None, line=line_no))
            continue
        if key in result.values:
            result.findings.append(Finding("duplicate-key", "error", f"Variable {key} is defined more than once.", key=key, line=line_no))
        result.values[key] = _decode_value(raw_value, line_no, result.findings)
        result.lines[key] = line_no
    return result


def parse_file(path: str | Path) -> ParsedEnv:
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{file_path} is not valid UTF-8") from exc
    except OSError as exc:
        raise ValueError(f"Cannot read {file_path}: {exc}") from exc
    return parse_text(text)
