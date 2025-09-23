# renders pinned-post text files from your YAML config
import os, yaml

CFG = "ops/gumroad-agent/config/gumroad.config.yaml"
OUT = "rendered_social"
os.makedirs(OUT, exist_ok=True)

with open(CFG, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

pay = (cfg.get("social", {}).get("ctas", {}) or {}).get("pay_link", "")
bundle = (cfg.get("social", {}).get("ctas", {}) or {}).get("gumroad_bundle_url", "")

def sub(s: str) -> str:
    return s.replace("{PAY_LINK}", pay).replace("{GUMROAD_BUNDLE_URL}", bundle).strip() + "\n"

ln = (cfg.get("social", {}).get("linkedin", {}) or {}).get("pin_post", "")
xx = (cfg.get("social", {}).get("x", {}) or {}).get("pin_post", "")

with open(f"{OUT}/linkedin_pin.txt", "w", encoding="utf-8") as f:
    f.write(sub(ln))
with open(f"{OUT}/x_pin.txt", "w", encoding="utf-8") as f:
    f.write(sub(xx))

print("Rendered:", f"{OUT}/linkedin_pin.txt", f"{OUT}/x_pin.txt")
