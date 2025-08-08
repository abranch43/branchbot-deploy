# branchbot-deploy

> **One-Click Deploy Revenue Tracker**  
> Instant API + Dashboard + PostgreSQL setup via Railway!

---

## 🚀 Deploy Now

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/YOUR-RAILWAY-TEMPLATE-LINK-HERE)

---

## ✅ What's Included

- **One-Click Railway Deploy:**  
  Provisions API, Dashboard, and PostgreSQL automatically.
- **Step-by-Step Setup:**  
  Deploy, configure webhooks, and go live!
- **Environment Variables Guide:**  
  All required and optional configs.
- **Webhook Configuration:**  
  Exact URLs for Stripe & Gumroad, plus test commands.
- **Project Structure:**  
  Visual map of the codebase.
- **Local Development:**  
  Easy instructions for running locally.

---

## 🛠️ Deploy Steps (Super Short)

1. **Click Deploy:**  
   - Use the Railway Deploy button above.

2. **Set Variables in Railway:**  
   - `STRIPE_WEBHOOK_SECRET` (starts with whsec_...)
   - `GUMROAD_WEBHOOK_SECRET` (any shared secret you’ll also use in Gumroad)
   - (optional) `OPENAI_API_KEY`, `SLACK_WEBHOOK_URL`

3. **Wait for branchberg-api to turn green**  
   - Copy its Public Domain.

4. **Health check:**  
   - Visit: `https://<API>/health`  
   - Should return: `{"status":"ok"}`

5. **Point webhooks to these endpoints:**  
   - **Stripe:** `https://<YOUR-API-DOMAIN>/webhooks/stripe`
   - **Gumroad:** `https://<YOUR-API-DOMAIN>/webhooks/gumroad`

6. **Open your dashboard service URL**  
   - Totals will auto-refresh every ~10s.

---

## 🕹️ Webhook Configuration

- **Stripe:**  
  - Go to Stripe Dashboard → Developers → Webhooks
  - Add endpoint:  
    ```
    https://<YOUR-API-DOMAIN>/webhooks/stripe
    ```
  - Use signing secret: `STRIPE_WEBHOOK_SECRET`

- **Gumroad:**  
  - Go to Gumroad Settings → Advanced → Webhooks
  - Add endpoint:  
    ```
    https://<YOUR-API-DOMAIN>/webhooks/gumroad
    ```
  - Use signing secret: `GUMROAD_WEBHOOK_SECRET`

---

## 🧪 Quick Live Test

**Stripe (from your machine):**
```bash
stripe listen --forward-to https://<YOUR-API-DOMAIN>/webhooks/stripe
stripe trigger checkout.session.completed
```

**Gumroad (test):**
```bash
curl -X POST https://<YOUR-API-DOMAIN>/webhooks/gumroad \
  -F seller_id=dummy -F product_id=toolkit -F email=tester@example.com \
  -F price=89700 -F currency=USD -F order_number=ORD123 \
  -F signature=$(python - <<'PY'
import hmac,hashlib;print(hmac.new(b'YOUR_SHARED_SECRET', b'ORD123', hashlib.sha256).hexdigest())
PY)
```

---

## ⚡ Project Structure

```
branchbot-deploy/
├── api/               # FastAPI backend (webhooks, DB)
├── dashboard/         # Streamlit dashboard (auto-refresh)
├── database/          # PostgreSQL models/migrations
├── README.md
├── requirements.txt
└── railway.json       # Railway project config
```

- **`api/`**: Handles Stripe & Gumroad webhooks, revenue calculations
- **`dashboard/`**: Live revenue, event feed (auto-refresh)
- **`database/`**: PostgreSQL schema & migrations

---

## 🧑‍💻 Local Development (Optional)

1. **Clone Repo:**
   ```bash
   git clone https://github.com/abranch43/branchbot-deploy.git
   cd branchbot-deploy
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run API Locally:**
   ```bash
   uvicorn api.main:app --reload
   ```

4. **Run Dashboard Locally:**
   ```bash
   streamlit run dashboard/main.py
   ```

5. **Set Local Environment Variables:**
   - Create a `.env` file, add your secrets:
     ```
     STRIPE_WEBHOOK_SECRET=your_stripe_secret
     GUMROAD_WEBHOOK_SECRET=your_gumroad_secret
     OPENAI_API_KEY=your_openai_key  # (optional)
     SLACK_WEBHOOK_URL=your_slack_url  # (optional)
     ```

---

## 💰 Live Revenue Tracking

Once deployed, your dashboard shows:

- **Real-time revenue metrics:**  
  - Today, This Week, All-Time totals
- **Live event feed:**  
  - Timestamps, amounts, event types
- **Auto-refresh:**  
  - Updates every 10 seconds
- **Test events:**  
  - Demo data for Stripe/Gumroad

---

## 🎯 What Happens When You Click Deploy?

- **Railway provisions:**
  - `branchberg-api` service (FastAPI backend)
  - `branchberg-dashboard` service (Streamlit dashboard)
  - **PostgreSQL** database (shared for both services)
  - **SSL Certificates** (HTTPS by default)

---

## ❓ FAQ

- **API 404?**  
  Make sure it’s `/webhooks/...` plural.

- **Dashboard shows $0?**  
  Trigger the tests above; then refresh.

- **Health not OK?**  
  Check Railway logs on branchberg-api; verify `DATABASE_URL` exists (Postgres plugin).

---

## 📝 License

MIT

---

> Ready for $50K/month live revenue tracking? Paste, commit, deploy – you're done!