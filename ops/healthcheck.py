import json
from datetime import datetime
from pathlib import Path


def read_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return {}


def main():
    latest = read_json("data/contracts/latest.json")
    meta = read_json("data/contracts/latest.meta.json")
    opps = read_json("data/opportunities.json")
    outdir = Path("data/output")
    csvs = sorted(outdir.glob("opps_*.csv")) if outdir.exists() else []
    print("=== BranchBot Health ===")
    print("Now UTC:", datetime.utcnow().isoformat() + "Z")
    print("Total last run:", meta.get("total") or latest.get("total"))
    print("New last run:", meta.get("new_count") or latest.get("new_count"))
    print("Items cached:", len(opps) if isinstance(opps, list) else 0)
    print("Latest CSV:", str(csvs[-1]) if csvs else "None")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
