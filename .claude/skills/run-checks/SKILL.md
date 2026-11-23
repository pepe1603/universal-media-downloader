---
name: run-checks
description: Run compile and tests before commit.
---
# Run Checks
1. Compile: `python -m py_compile src/main.py src/core/*.py src/storage/*.py src/platforms/*.py`
2. Tests: `python -m pytest tests -q`
3. Report failures; fix before commit.