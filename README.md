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

## 🛠️ Step-by-Step Setup

1. **Copy & Commit:**  
   - Paste this `README.md` into your repo.
   - Commit and push to GitHub.

2. **Click Deploy:**  
   - Hit the Railway Deploy button above.

3. **Set Environment Variables:**  
   In Railway dashboard, set:
   - `STRIPE_WEBHOOK_SECRET` (**required**)
   - `GUMROAD_WEBHOOK_SECRET` (**required**)
   - `OPENAI_API_KEY` *(optional, for advanced features)*
   - `SLACK_WEBHOOK_URL` *(optional, for notifications)*

4. **Configure Webhooks:**
   - Get your API URL from the Railway dashboard (e.g., `https://branchberg-api.up.railway.app`)
   - Set Stripe webhook endpoint to:
     ```
     https://branchberg-api.up.railway.app/webhook/stripe
     ```
   - Set Gumroad webhook endpoint to:
     ```
     https://branchberg-api.up.railway.app/webhook/gumroad
     ```

5. **Test End-to-End:**
   - Use these curl commands to send test events:

     **Stripe Test:**
     ```bash
     curl -X POST https://branchberg-api.up.railway.app/webhook/stripe \
       -H "Content-Type: application/json" \
       -d '{"type":"payment_intent.succeeded","data":{"object":{"amount":5000}}}'
     ```

     **Gumroad Test:**
     ```bash
     curl -X POST https://branchberg-api.up.railway.app/webhook/gumroad \
       -H "Content-Type: application/json" \
       -d '{"sale":{"price":2000,"created_at":"2025-08-08T20:32:53Z"}}'
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

## 🕹️ Webhook Configuration

- **Stripe:**  
  - Go to Stripe Dashboard → Developers → Webhooks
  - Add endpoint:  
    ```
    https://branchberg-api.up.railway.app/webhook/stripe
    ```
  - Use signing secret: `STRIPE_WEBHOOK_SECRET`

- **Gumroad:**  
  - Go to Gumroad Settings → Advanced → Webhooks
  - Add endpoint:  
    ```
    https://branchberg-api.up.railway.app/webhook/gumroad
    ```
  - Use signing secret: `GUMROAD_WEBHOOK_SECRET`

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

- **Can I use only Stripe or only Gumroad?**  
  Yes. Set only the relevant webhook secret and endpoint.

- **Is local dev required?**  
  No. One-click deploy is all you need, but local dev is supported!

- **How do I test?**  
  Use the provided curl commands or trigger real webhooks from Stripe/Gumroad.

---

## 📝 License

MIT

---

> Ready for $50K/month live revenue tracking? Paste, commit, deploy – you're done!