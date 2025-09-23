# agents/gumroad_sync.py (v3 – token optional; bundle via Playwright)
import os, sys, yaml, requests

API_BASE = "https://api.gumroad.com/v2"

def api_request(method, path, token, **kwargs):
    url = f"{API_BASE}{path}"
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    r = requests.request(method, url, headers=headers, timeout=60, **kwargs)
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {r.status_code} {r.text[:300]}")
    return r.json()

def list_products(token):
    return api_request("GET", "/products", token).get("products", [])

def find_by_handle(items, handle):
    for p in items:
        if p.get("custom_permalink") == handle or str(p.get("short_url","")).endswith("/"+handle):
            return p
    return None

def upsert_product(token, spec):
    existing = find_by_handle(list_products(token), spec["handle"])
    payload = {
        "name": spec["title"],
        "price": spec["price_cents"],
        "custom_permalink": spec["handle"],
        "description": spec.get("description_md",""),
        "published": bool(spec.get("published", True)),
    }
    if existing:
        pid = existing["id"]
        api_request("PUT", f"/products/{pid}", token, json=payload)
        print(f"[API] Updated: {spec['title']} ({pid})")
    else:
        res = api_request("POST", "/products", token, json=payload)
        print(f"[API] Created: {spec['title']} ({res.get('product',{}).get('id')})")

def ensure_discount(token, code, percent_off, active=True):
    try:
        api_request("POST", "/coupons", token, json={
            "name": code, "percent_off": int(percent_off), "active": bool(active)
        })
        print(f"[API] Ensured coupon {code}")
    except Exception as e:
        print(f"[WARN] Coupon ensure varies by account: {e}")

def set_affiliates_per_product(token, percent):
    for p in list_products(token):
        pid = p["id"]
        try:
            api_request("PUT", f"/products/{pid}", token,
                        json={"affiliate": {"enabled": True, "percent": int(percent)}})
            print(f"[API] Affiliates {percent}% -> {p['name']}")
        except Exception as e:
            print(f"[WARN] Affiliate update skipped for {p['name']}: {e}")

def make_bundle_via_playwright(spec):
    email = os.environ.get("GUMROAD_EMAIL")
    password = os.environ.get("GUMROAD_PASSWORD")
    if not email or not password:
        print("[SKIP] Bundle needs GUMROAD_EMAIL/PASSWORD secrets.")
        return
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("[SKIP] Playwright not installed.")
        return

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://gumroad.com/login")
        page.fill('input[name="user[email]"]', email)
        page.fill('input[name="user[password]"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        page.goto("https://gumroad.com/products/new?type=bundle")
        page.wait_for_selector('input[name="product[name]"]')
        page.fill('input[name="product[name]"]', spec["title"])
        page.fill('input[name="product[custom_permalink]"]', spec["handle"])
        page.fill('input[name="product[price]"]', str(spec["price_cents"]))
        for h in spec.get("includes_handles", []):
            page.click('button:has-text("Add products")')
            page.fill('input[placeholder="Search products"]', h)
            page.wait_for_timeout(800)
            page.click('div[role="option"]')
        page.fill('textarea[name="product[description]"]', spec.get("description_md","")[:4000])
        page.click('button:has-text("Create")')
        page.wait_for_load_state("networkidle")
        print(f"[PW] Bundle attempted: {spec['title']}")
        browser.close()

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="ops/gumroad-agent/config/gumroad.config.yaml")
    args = ap.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    token = (os.environ.get("GUMROAD_ACCESS_TOKEN") or "").strip()
    if token:
        for d in cfg.get("discounts", []):
            ensure_discount(token, d["code"], d["percent_off"], d.get("active", True))
        for item in cfg.get("products", []):
            if item.get("kind") == "product":
                upsert_product(token, item)
        aff = (cfg.get("storefront") or {}).get("affiliates", {})
        if aff.get("enabled"):
            set_affiliates_per_product(token, int(aff.get("default_percent", 25)))
    else:
        print("[INFO] No token: skipping API sync; will run bundle automation only.")

    # Always try bundles via Playwright
    for item in cfg.get("products", []):
        if item.get("kind") == "bundle":
            make_bundle_via_playwright(item)

    print("Sync complete.")

if __name__ == "__main__":
    main()
