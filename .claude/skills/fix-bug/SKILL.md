---
name: fix-bug
description: Resolve a bug from docs/BUGS.md following workflow.
---
# Fix Bug
1. Read docs/BUGS.md; pick highest severity pending bug.
2. Determine branch: Termux (BUG-01..05) -> termux; Terminal (BUG-06..15) -> terminal.
3. `git checkout <branch> && git merge --ff-only develop` (if needed).
4. Implement fix (minimal).
5. Run run-checks.
6. Commit `fix(BUG-XX): short description`.
7. Mark bug Resolved in docs/BUGS.md; commit `docs(BUGS): mark BUG-XX as resolved`.
8. Push branch; merge to develop (confirm).