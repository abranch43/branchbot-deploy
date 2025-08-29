from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def build_snapshot() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Funnels Pulse",
        f"_Generated: {now}_",
        "",
        "## Summary",
        "- Gumroad: 0 new messages, 0 sales",
        "- Fiverr: 0 new briefs",
        "- Upwork: 0 relevant jobs",
        "",
        "## Notes",
        "This is a scaffold snapshot. Replace with real adapters and data.",
    ]
    return "\n".join(lines) + "\n"


def build_snapshot_from_data(*, gumroad_messages: int, gumroad_sales: int, fiverr_briefs: int, upwork_jobs: int) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Funnels Pulse",
        f"_Generated: {now}_",
        "",
        "## Summary",
        f"- Gumroad: {gumroad_messages} new messages, {gumroad_sales} sales",
        f"- Fiverr: {fiverr_briefs} new briefs",
        f"- Upwork: {upwork_jobs} relevant jobs",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Funnels Pulse snapshot (scaffold).")
    parser.add_argument(
        "--out", default="out/funnels/funnels_snapshot.md", help="Output markdown path"
    )
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_snapshot(), encoding="utf-8")
    print(f"Wrote snapshot: {out_path.resolve()}")


if __name__ == "__main__":
    main()
