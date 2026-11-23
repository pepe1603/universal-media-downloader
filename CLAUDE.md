# UMD (Universal Media Downloader) — Claude Code guide

## Stack
Python 3.12+, yt-dlp, FFmpeg, mutagen, SQLite, Rich, Pydantic. Entry point: `src/main.py`.

## Layout
- `src/core/`: downloader, converter, metadata, exporter, dependencies, environment, file_organizer, cookies
- `src/platforms/detector.py`, `src/storage/database.py`, `src/ui/`
- `tests/`, `docs/` (BUGS.md, WORKFLOW.md, ANDROID_GUIDE.md)

## Workflow (mandatory)
Read `docs/WORKFLOW.md` before changes.
- Branches: `main` (release, no direct push), `develop` (integration), `termux`/`terminal` (env fixes).
- One commit per bug; format `tipo(alcance): descripción` (<=72 chars).
- Push to `main` only with explicit user confirmation.
- Update `docs/BUGS.md` status table after fixing.

## Commands
- Compile: `python -m py_compile src/main.py src/core/*.py src/storage/*.py src/platforms/*.py`
- Tests: `python -m pytest tests -q`
- Run: `python src/main.py`

## Rules
- No secrets/cookies in commits (`cookies/` gitignored).
- Never `shell=True` with user input; subprocess uses arg lists + `encoding="utf-8", errors="replace"`.
- Validate/normalize paths with pathlib; prevent path traversal.
- Support Termux/Windows/Linux/macOS; don't assume UTF-8 console.
- Update `requirements.txt` and `requirements.lock` together.
- Small, focused edits; run checks before commit.