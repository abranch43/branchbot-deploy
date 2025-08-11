from __future__ import annotations

import json
import os
import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetsSink:
    def __init__(self) -> None:
        self.creds_json = os.getenv("GOOGLE_SHEETS_JSON")
        self.sheet_name = os.getenv("GOOGLE_SHEETS_NAME", "BranchBot Contracts")

    def write(self, csv_path: str) -> None:
        if not self.creds_json:
            return
        info = json.loads(self.creds_json)
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        gc = gspread.authorize(creds)
        try:
            sh = gc.open(self.sheet_name)
        except Exception:
            sh = gc.create(self.sheet_name)
        with open(csv_path, "r", encoding="utf-8") as f:
            content = f.read()
        gc.import_csv(sh.id, content)