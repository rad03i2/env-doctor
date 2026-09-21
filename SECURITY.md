# Security Policy

## Supported version

The latest release on the default branch is supported.

## Security model

Env Doctor is intentionally local and does not implement networking or telemetry. It should never print dotenv or process-environment values in findings or JSON reports. The tool is a configuration linter, not a credential vault or a guarantee that a value is non-secret.

## Reporting a vulnerability

Please report security concerns through GitHub's private vulnerability reporting feature when available. Do not open a public issue containing credentials, environment dumps, private paths, or other sensitive data.

When reporting, include a minimal synthetic reproduction and the affected version. Never attach a real `.env` file.

## Scope

Relevant issues include unintended disclosure of environment values, unsafe parsing behavior, command execution, or a path that causes Env Doctor to transmit data. False positives or false negatives in heuristic placeholder/secret warnings are correctness issues but are not automatically security vulnerabilities.

Maintainer: **Radwan Abdulhadi Ahmed / رضوان عبدالهادي أحمد / @rad03i2**.
