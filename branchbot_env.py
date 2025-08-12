from pathlib import Path


def load_env():
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    for p in [Path(".env"), Path.home() / ".branchbot.env"]:
        if p.exists():
            load_dotenv(p, override=False)


load_env()
