from fastapi import FastAPI, Request
import os

app = FastAPI(title="Branchberg API", description="Revenue platform API with webhooks", version="2.0")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    event = await request.json()
    # Save event to DB (stub)
    return {"received": True, "source": "stripe", "event": event}

@app.post("/webhooks/gumroad")
async def gumroad_webhook(request: Request):
    secret = os.getenv("GUMROAD_WEBHOOK_SECRET", "")
    event = await request.json()
    # Save event to DB (stub)
    return {"received": True, "source": "gumroad", "event": event}