# Workflow rules
- Read docs/WORKFLOW.md before any change.
- Branches: main (no direct push), develop, termux, terminal.
- Bugs: Termux BUG-01..05 -> termux; Terminal BUG-06..15 -> terminal.
- One commit per bug: `fix(BUG-XX): short description`.
- Before push: py_compile + pytest.
- Never push to main without user confirmation.
- Update docs/BUGS.md status table.