from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class Finding:
    code: str
    severity: Severity
    message: str
    key: str | None = None
    line: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Report:
    source: str
    findings: list[Finding] = field(default_factory=list)
    variables: int = 0

    @property
    def errors(self) -> int:
        return sum(item.severity == "error" for item in self.findings)

    @property
    def warnings(self) -> int:
        return sum(item.severity == "warning" for item in self.findings)

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "variables": self.variables,
            "summary": {"errors": self.errors, "warnings": self.warnings, "findings": len(self.findings)},
            "findings": [item.to_dict() for item in self.findings],
        }
