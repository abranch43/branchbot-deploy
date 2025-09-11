import os

import requests


def main():
    token = os.environ["NOTION_TOKEN"]
    version = os.environ.get("NOTION_VERSION", "2022-06-28")
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": version,
        "Content-Type": "application/json",
    }
    resp = requests.get("https://api.notion.com/v1/users/me", headers=headers)
    resp.raise_for_status()
    print("Bot OK:", resp.json().get("bot", {}).get("owner"))

    db_id = os.environ.get("NOTION_DATABASE_ID")
    if db_id:
        db_resp = requests.post(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            headers=headers,
            json={},
        )
        if db_resp.status_code == 403:
            print("Database not shared with integration.")
        else:
            db_resp.raise_for_status()
            print("Database query OK")


if __name__ == "__main__":
    main()
