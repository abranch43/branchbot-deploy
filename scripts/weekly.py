import os
import re
import sys
import requests


PLACEHOLDER_PATTERNS = (
    r"\{database_id\}",
    r"<database_id>",
    r"\{.*\}",
    r"<.*>",
)


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    if any(re.fullmatch(pat, value, flags=re.IGNORECASE) for pat in PLACEHOLDER_PATTERNS):
        raise ValueError(f"Environment variable {name} is still a placeholder; set a real value.")
    return value

def is_probable_notion_id(value: str) -> bool:
    # Accept 32-char (no dashes) or 36-char (with dashes) UUID-like strings
    return bool(
        re.fullmatch(r"[0-9a-fA-F]{32}", value)
        or re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", value)
    )

def main():
    try:
        token = require_env("NOTION_TOKEN")
        db_id = require_env("NOTION_DATABASE_ID")
    except ValueError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not is_probable_notion_id(db_id):
        print(
            "Config error: NOTION_DATABASE_ID does not look like a Notion database UUID "
            "(expected 32 hex chars, with or without dashes).",
            file=sys.stderr,
        )
        sys.exit(1)

    version = os.environ.get("NOTION_VERSION", "2022-06-28")
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": version,
        "Content-Type": "application/json",
    }

    # Check integration access
    resp = requests.get("https://api.notion.com/v1/users/me", headers=headers)
    resp.raise_for_status()
    print("Bot OK:", resp.json().get("bot", {}).get("owner"))

    # Query database
    db_resp = requests.post(
        f"https://api.notion.com/v1/databases/{db_id}/query",
        headers=headers,
        json={},
    )
    if db_resp.status_code == 403:
        print("Database not shared with integration.")
    elif db_resp.status_code == 404:
        print(
            "Database not found (404). Verify NOTION_DATABASE_ID is correct and corresponds to a shared database."
        )
        db_resp.raise_for_status()
    else:
        db_resp.raise_for_status()
        print("Database query OK")


if __name__ == "__main__":
    main()