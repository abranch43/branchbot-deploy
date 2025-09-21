"""BranchBot CLI (propose-only, audited)."""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

AUDIT_DIR = Path(".branchbot") / "audit"
PROPOSALS_DIR = Path(".branchbot") / "proposals"

def _ensure(p: Path): p.mkdir(parents=True, exist_ok=True)

def _audit(action: str, status: str, details: Dict[str, object]) -> None:
    _ensure(AUDIT_DIR)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")
    (AUDIT_DIR / f"{ts}_{action}.json").write_text(
        json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action, "status": status, "details": details
        }, indent=2)
    )

def cmd_status(_: argparse.Namespace) -> int:
    r = subprocess.run(["git","status","--short"], text=True, capture_output=True)
    print(r.stdout or "Working tree clean.")
    _audit("status","success",{"returncode": r.returncode, "stdout": r.stdout, "stderr": r.stderr})
    return 0

def cmd_find(args: argparse.Namespace) -> int:
    query = args.query
    base = Path.cwd()
    matches: List[str] = []
    for p in base.rglob("*"):
        if not p.is_file(): continue
        if any(part in {".git",".branchbot"} for part in p.parts): continue
        try:
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                if query in line:
                    matches.append(f"{p.relative_to(base)}:{i}:{line.strip()}")
        except Exception:
            pass
    for m in matches: print(m)
    print(f"Found {len(matches)} match(es) for '{query}'.")
    _audit("find","success",{"query": query, "match_count": len(matches), "sample": matches[:100]})
    return 0

def cmd_propose_fix(args: argparse.Namespace) -> int:
    _ensure(PROPOSALS_DIR)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    payload = {
        "timestamp": datetime.utcnow().isoformat()+"Z",
        "target": args.target,
        "summary": args.summary,
        "instructions": "Generate a unified .patch addressing the summary. Do NOT edit files directly.",
        "requested_by": os.getenv("USER") or os.getenv("USERNAME"),
    }
    path = PROPOSALS_DIR / f"{ts}.json"
    path.write_text(json.dumps(payload, indent=2))
    print(f"Proposal recorded → {path}")
    _audit("propose-fix","success",{"proposal": str(path), **payload})
    return 0

def cmd_apply(args: argparse.Namespace) -> int:
    patch = Path(args.patch)
    if not patch.exists():
        print(f"Patch not found: {patch}", file=sys.stderr)
        _audit("apply","error",{"error":"patch missing","patch":str(patch)}); return 1
    r = subprocess.run(["git","apply","--index",str(patch)], text=True, capture_output=True)
    if r.returncode == 0:
        print("Patch applied and staged. Review with: git diff --staged")
        status = "success"
    else:
        print(r.stderr or "Failed to apply patch.", file=sys.stderr); status = "error"
    _audit("apply", status, {"patch":str(patch), "rc":r.returncode, "stdout":r.stdout, "stderr":r.stderr})
    return r.returncode

def cmd_run_tests(args: argparse.Namespace) -> int:
    cmd = args.cmd or "pytest -q"
    r = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if r.stdout: print(r.stdout, end="")
    if r.stderr: print(r.stderr, end="", file=sys.stderr)
    _audit("run-tests", "success" if r.returncode==0 else "error",
           {"cmd":cmd,"rc":r.returncode,"stdout":r.stdout,"stderr":r.stderr})
    return r.returncode

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="branchbot", description="BranchBot CLI (propose-only)")
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("status").set_defaults(func=cmd_status)
    f = s.add_parser("find"); f.add_argument("query"); f.set_defaults(func=cmd_find)
    pf = s.add_parser("propose-fix"); pf.add_argument("target"); pf.add_argument("--summary", required=True); pf.set_defaults(func=cmd_propose_fix)
    ap = s.add_parser("apply"); ap.add_argument("patch"); ap.set_defaults(func=cmd_apply)
    rt = s.add_parser("run-tests"); rt.add_argument("--cmd"); rt.set_defaults(func=cmd_run_tests)
    return p

def main(argv: List[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())