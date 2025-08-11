# Security Notes

- Secrets are never committed. Use environment variables and CI secrets.
- `.env.template` lists required keys; copy to `.env` locally and ensure your shell loads it.
- CI uses GitHub Actions repository secrets; workflow has minimal permissions.
- Email SMTP credentials should be dedicated for this bot and rotated periodically.
- Notion and Google credentials are optional; use least privilege scopes.
- Logs contain minimal metadata and rotate to avoid unbounded growth.
- Lead data includes only contact info necessary to follow up. Do not store sensitive PII.