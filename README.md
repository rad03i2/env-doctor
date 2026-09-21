# Env Doctor

A local, dependency-free Python CLI that audits development environment configuration and `.env` files for common mistakes, missing variables, unsafe values, duplicates, and configuration drift.

**Author:** Radwan Abdulhadi Ahmed · رضوان عبدالهادي أحمد · GitHub: @rad03i2

> Privacy first: Env Doctor performs all analysis locally. It does not send environment values anywhere and masks values in reports.

## Why it exists

Environment configuration failures are often discovered only after an application starts. Env Doctor provides a small, scriptable preflight check that can run locally or in CI without requiring a cloud service or third-party runtime dependency.

## Features

- Parse dotenv-style files with comments, `export KEY=value`, quoted values, and inline comments.
- Detect duplicate keys, malformed lines, invalid variable names, empty values, and placeholder values.
- Compare a real environment file against an `.env.example` contract.
- Detect variables that are missing or unexpectedly present.
- Flag likely sensitive values stored in `.env.example`.
- Audit the current process environment against an example contract without printing values.
- Machine-readable JSON output for CI and automation.
- Configurable strict mode: warnings can fail a check.
- Exit codes designed for scripting.
- Standard-library-only runtime; Python 3.10+.

## Requirements

- Python 3.10 or newer
- No runtime dependencies

## Installation

From the repository:

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -e .
```

## Usage

Audit one dotenv file:

```bash
env-doctor check .env
```

Compare a file with its documented contract:

```bash
env-doctor check .env --example .env.example
```

Audit the current process environment against the example:

```bash
env-doctor process --example .env.example
```

Produce JSON suitable for CI:

```bash
env-doctor check .env --example .env.example --json
```

Treat warnings as failures:

```bash
env-doctor check .env --strict
```

Show version:

```bash
env-doctor --version
```

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | No failing findings |
| `1` | Errors found, or warnings found in `--strict` mode |
| `2` | Invalid CLI input / unreadable file |

## Configuration

Env Doctor intentionally has no hidden configuration file and needs no environment variables of its own. Behavior is controlled by CLI options so CI runs remain explicit and reproducible.

## Example

Given `.env.example`:

```dotenv
DATABASE_URL=postgresql://localhost/app
API_TOKEN=change-me
PORT=8000
```

and `.env`:

```dotenv
DATABASE_URL=postgresql://localhost/app
PORT=
EXTRA_FLAG=true
```

`env-doctor check .env --example .env.example` reports the missing `API_TOKEN`, empty `PORT`, unexpected `EXTRA_FLAG`, and warns that the example contains a placeholder value.

## Project structure

```text
env-doctor/
├── src/env_doctor/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── model.py
│   ├── parser.py
│   └── audit.py
├── tests/
│   └── test_env_doctor.py
├── .github/workflows/ci.yml
├── pyproject.toml
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

## Testing

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

CI runs the same validation on supported Python versions across Linux, Windows, and macOS.

## Preview / screenshots

Env Doctor is a CLI, so screenshots are optional. For a portfolio preview, capture `env-doctor check .env --example .env.example` using a deliberately synthetic configuration file. Never publish a terminal screenshot containing real credentials.

## Security and privacy

- Analysis is local and no telemetry is implemented.
- Reports show variable names and finding descriptions, not secret values.
- The example-secret heuristic is conservative and may produce false positives.
- Env Doctor is a configuration linter, **not** a secret-management system or a complete secret scanner.
- Do not commit real `.env` files; `.gitignore` excludes common local environment files.

See [SECURITY.md](SECURITY.md) for reporting guidance.

## Limitations

- Dotenv syntax differs among frameworks; the parser intentionally supports a practical common subset rather than shell evaluation.
- Variable interpolation such as `${NAME}` is preserved as text and is not executed.
- Multiline quoted values are not supported.
- Secret detection is heuristic and cannot prove that a value is safe or compromised.
- Process auditing checks presence/emptiness only; it never exports process values.

## Optional roadmap

Future work may add opt-in schema types (integer/URL/boolean), allow/deny patterns, and SARIF output. These are not required for the current core workflow.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Keep changes focused, tested, dependency-conscious, and privacy-preserving.

## License

MIT License. See [LICENSE](LICENSE).

## Author

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# العربية

## نظرة عامة

**Env Doctor** أداة سطر أوامر محلية مكتوبة ببايثون لفحص إعدادات بيئة التطوير وملفات `.env` قبل تشغيل التطبيق. تكشف الأخطاء الشائعة مثل المتغيرات المفقودة، القيم الفارغة، الأسطر غير الصالحة، المفاتيح المكررة، القيم التجريبية، والاختلاف بين ملف الإعداد الحقيقي وملف `.env.example`.

تعمل الأداة محليًا بالكامل ولا ترسل قيم البيئة إلى أي خدمة خارجية، كما أن التقارير لا تطبع قيم المتغيرات الحساسة.

## لماذا المشروع؟

كثير من أخطاء الإعداد لا تظهر إلا عند تشغيل التطبيق أو نشره. يوفّر Env Doctor فحصًا مسبقًا صغيرًا وقابلًا للأتمتة يمكن استخدامه محليًا أو داخل CI من دون خدمة سحابية أو اعتماديات تشغيل خارجية.

## الميزات

- قراءة صيغة dotenv الشائعة بما فيها التعليقات و`export KEY=value` والقيم المقتبسة.
- اكتشاف المفاتيح المكررة والأسطر غير الصحيحة وأسماء المتغيرات غير الصالحة والقيم الفارغة والتجريبية.
- مقارنة `.env` مع `.env.example` باعتباره عقد الإعداد المتوقع.
- كشف المتغيرات المفقودة والمتغيرات الإضافية غير الموثقة.
- التحذير من القيم التي تبدو حساسة داخل ملف المثال.
- فحص بيئة العملية الحالية مقابل ملف المثال من دون طباعة القيم.
- إخراج JSON مناسب للأتمتة وCI.
- وضع `--strict` لاعتبار التحذيرات فشلًا.
- رموز خروج واضحة للسكربتات.
- لا توجد اعتماديات تشغيل خارج مكتبة بايثون القياسية.

## المتطلبات والتثبيت

يتطلب Python 3.10 أو أحدث:

```bash
python -m pip install .
```

للتطوير:

```bash
python -m pip install -e .
```

## الاستخدام

فحص ملف واحد:

```bash
env-doctor check .env
```

مقارنة الملف مع المثال:

```bash
env-doctor check .env --example .env.example
```

فحص متغيرات العملية الحالية:

```bash
env-doctor process --example .env.example
```

إخراج JSON:

```bash
env-doctor check .env --example .env.example --json
```

اعتبار التحذيرات أخطاء:

```bash
env-doctor check .env --strict
```

## الإعداد

لا تحتاج الأداة إلى ملف إعداد خاص أو مفاتيح API أو متغيرات بيئة خاصة بها. جميع الخيارات صريحة من خلال CLI حتى تبقى عمليات CI قابلة للتكرار.

## بنية المشروع

الكود الأساسي موجود في `src/env_doctor`، والاختبارات في `tests`، وملف CI في `.github/workflows/ci.yml`. يشرح `SECURITY.md` سياسة الأمان و`CONTRIBUTING.md` طريقة المساهمة.

## الاختبارات

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

## المعاينة

المشروع أداة CLI ولا يحتاج واجهة رسومية. إذا أُضيفت صورة للمشروع، يجب استخدام ملف إعداد تجريبي فقط وعدم إظهار أي بيانات اعتماد حقيقية في لقطة الشاشة.

## الخصوصية والأمان

- الفحص محلي ولا توجد Telemetry.
- لا يطبع التقرير قيم المتغيرات.
- اكتشاف الأسرار داخل ملف المثال تقريبي وقد يعطي تحذيرات زائدة.
- الأداة مدقق إعدادات وليست مدير أسرار ولا بديلًا عن أدوات إدارة الأسرار المتخصصة.
- لا ينبغي رفع ملف `.env` الحقيقي إلى Git، وقد تم استبعاده في `.gitignore`.

## القيود

- تدعم الأداة مجموعة عملية مشتركة من صيغة dotenv وليست مفسر shell.
- لا تنفذ `${NAME}` ولا توسع المتغيرات.
- القيم المقتبسة متعددة الأسطر غير مدعومة.
- اكتشاف القيم الحساسة تقريبي.
- فحص بيئة العملية يتحقق من الوجود والفراغ فقط ولا يعرض القيم.

## التطوير المستقبلي الاختياري

يمكن مستقبلًا إضافة مخططات أنواع اختيارية وقواعد سماح/منع وإخراج SARIF، لكن الوظائف الأساسية الحالية لا تعتمد عليها.

## المساهمة والترخيص

راجع [CONTRIBUTING.md](CONTRIBUTING.md) للمساهمة. المشروع مرخص برخصة MIT الموجودة في [LICENSE](LICENSE).

## المؤلف

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
