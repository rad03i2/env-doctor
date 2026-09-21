import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from env_doctor.audit import audit_file, audit_process
from env_doctor.cli import main
from env_doctor.parser import parse_text


class ParserTests(unittest.TestCase):
    def test_parses_common_dotenv_syntax(self):
        parsed = parse_text('A=one\nexport B="two words"\nC=value # note\nD=\'literal value\'\n')
        self.assertEqual(parsed.values, {"A": "one", "B": "two words", "C": "value", "D": "literal value"})
        self.assertEqual(parsed.findings, [])

    def test_reports_malformed_invalid_and_duplicate_entries(self):
        parsed = parse_text("NO_EQUALS\n1BAD=x\nA=1\nA=2\n")
        self.assertEqual([f.code for f in parsed.findings], ["malformed-line", "invalid-name", "duplicate-key"])
        self.assertEqual(parsed.values["A"], "2")

    def test_reports_unclosed_quote(self):
        parsed = parse_text('A="broken\n')
        self.assertEqual(parsed.findings[0].code, "unclosed-quote")


class AuditTests(unittest.TestCase):
    def test_contract_detects_missing_unexpected_and_empty(self):
        actual = parse_text("A=\nEXTRA=yes\n")
        example = parse_text("A=sample\nB=change-me\n")
        report = audit_file(actual, ".env", example)
        codes = {f.code for f in report.findings}
        self.assertTrue({"empty-value", "missing-variable", "unexpected-variable", "placeholder-value"}.issubset(codes))
        self.assertGreaterEqual(report.errors, 2)

    def test_example_sensitive_concrete_value_is_warning(self):
        report = audit_file(parse_text("API_TOKEN=local\n"), ".env", parse_text("API_TOKEN=abc123-real-looking\n"))
        self.assertIn("example-secret-risk", [f.code for f in report.findings])

    def test_process_audit_does_not_export_values(self):
        example = parse_text("A=placeholder\nB=placeholder\n")
        report = audit_process(example, {"A": "top-secret", "B": ""})
        encoded = json.dumps(report.to_dict())
        self.assertNotIn("top-secret", encoded)
        self.assertIn("empty-value", encoded)


class CliTests(unittest.TestCase):
    def test_json_cli_and_exit_code(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            actual = root / ".env"
            example = root / ".env.example"
            actual.write_text("A=ok\n", encoding="utf-8")
            example.write_text("A=placeholder\nB=placeholder\n", encoding="utf-8")
            out = StringIO()
            with redirect_stdout(out):
                code = main(["check", str(actual), "--example", str(example), "--json"])
            payload = json.loads(out.getvalue())
            self.assertEqual(code, 1)
            self.assertEqual(payload["summary"]["errors"], 1)
            self.assertEqual(payload["source"], str(actual))

    def test_strict_turns_warning_into_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / ".env"
            path.write_text("A=change-me\n", encoding="utf-8")
            with redirect_stdout(StringIO()):
                self.assertEqual(main(["check", str(path)]), 0)
                self.assertEqual(main(["check", str(path), "--strict"]), 1)

    def test_missing_file_is_usage_error(self):
        with patch("sys.stderr", new=StringIO()):
            self.assertEqual(main(["check", "definitely-not-present.env"]), 2)


if __name__ == "__main__":
    unittest.main()
