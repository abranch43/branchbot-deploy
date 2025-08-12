# Leadgen Site

- Next.js app with simple landing page and lead form
- API route `/api/lead` appends to `../../data/leads.json` (best effort) and emails via SMTP
- Stripe Buy Now button uses `STRIPE_CHECKOUT_URL`

## Local Dev
```bash
cd apps/leadgen-site
npm install
npm run dev
```

Set environment variables (use repo `.env` or export):
- EMAIL_FROM, EMAIL_TO, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
- STRIPE_CHECKOUT_URL (or NEXT_PUBLIC_STRIPE_CHECKOUT_URL)

## Deploy (Vercel)
- Connect repo to Vercel
- Add the above environment variables
- Deploy. Note: filesystem writes are ephemeral on Vercel; rely on email for lead capture.