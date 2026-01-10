import os
import warnings


def get_notion_database_id():
    db = os.getenv("NOTION_DATABASE_ID")
    legacy = os.getenv("NOTION_DB_ID")
    if not db and legacy:
        warnings.warn(
            "NOTION_DB_ID is deprecated; use NOTION_DATABASE_ID", RuntimeWarning
        )
        db = legacy
    if not db:
        raise ValueError("NOTION_DATABASE_ID is not set")
    return db
