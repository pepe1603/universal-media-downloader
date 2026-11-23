# Security rules
- Never commit secrets or cookies (cookies/ gitignored).
- No shell=True with user input; use arg lists.
- subprocess: encoding="utf-8", errors="replace".
- Validate/normalize paths; prevent traversal.
- Sanitize filenames for cross-platform safety.
- Don't log cookie contents.