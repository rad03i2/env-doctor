# Contributing to Env Doctor

Thank you for improving Env Doctor.

## Development

1. Use Python 3.10+.
2. Create a virtual environment.
3. Run `python -m pip install -e .`.
4. Make a focused change.
5. Add or update tests.
6. Run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

## Guidelines

- Keep the runtime dependency-free unless a dependency is clearly justified.
- Never add real credentials, `.env` files, tokens, or private data to fixtures.
- Reports must not expose environment values.
- Document behavior changes in both English and Arabic README sections when user-facing behavior changes.
- Keep examples synthetic and reproducible.

## Author

Maintained by **Radwan Abdulhadi Ahmed (رضوان عبدالهادي أحمد), @rad03i2**.
