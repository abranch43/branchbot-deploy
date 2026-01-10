# Universal Income Ingest - Quick Start Guide

Get started with the Universal Income Ingest feature in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Environment

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
# For development (SQLite):
DATABASE_URL=sqlite:///./branchbot.db

# For production (PostgreSQL):
# DATABASE_URL=postgresql://user:password@localhost/branchbot
```

## Step 3: Start the API

```bash
uvicorn branchberg.app.main:app --reload
```

The API will start on http://localhost:8000

## Step 4: Start the Dashboard

In a new terminal:

```bash
export API_URL=http://localhost:8000
streamlit run branchberg/dashboard/streamlit_app.py
```

The dashboard will open in your browser at http://localhost:8501

## Step 5: Test It Out!

### Add Your First Transaction

1. Go to http://localhost:8501
2. Select "Income Ingest" from the sidebar
3. Fill in the manual transaction form:
   - Amount: $100.00
   - Entity: A+ Enterprise LLC
   - Description: First test transaction
4. Click "Add Transaction"

You should see a success message and the revenue metrics will update!

### Upload CSV Transactions

1. Create a CSV file `test.csv`:
```csv
amount,email,entity,description
50.00,alice@test.com,A+ Enterprise LLC,Consulting
75.50,bob@test.com,Legacy Unchained Inc,Product sale
125.00,charlie@test.com,A+ Enterprise LLC,Service fee
```

2. In the dashboard, use the CSV Upload section
3. Select your CSV file
4. Map the columns:
   - Amount Column: amount
   - Email Column: email
   - Entity Column: entity
   - Description Column: description
5. Click "Upload & Process CSV"

### View Your Data

Switch to the "Transaction History" page to see all your transactions!

## API Usage Examples

### Using curl

```bash
# Add a transaction
curl -X POST http://localhost:8000/ingest/manual \
  -H "Content-Type: application/json" \
  -d '{"amount": 99.99, "currency": "USD"}'

# Get summary
curl http://localhost:8000/revenue/summary

# Get recent transactions
curl http://localhost:8000/revenue/events?limit=5
```

### Using Python

```python
import requests

# Add a transaction
response = requests.post(
    "http://localhost:8000/ingest/manual",
    json={
        "amount": 199.99,
        "customer_email": "customer@example.com",
        "entity": "A+ Enterprise LLC",
        "description": "Monthly subscription"
    }
)
print(response.json())

# Get summary
summary = requests.get("http://localhost:8000/revenue/summary").json()
print(f"Total revenue: ${summary['total_dollars']}")
print(f"Transaction count: {summary['count']}")
```

## Next Steps

- Read the full documentation: `docs/INCOME_INGEST.md`
- Check out the API docs: http://localhost:8000/docs
- Review AGENTS.md for future webhook integration plans
- Set up a production PostgreSQL database
- Deploy to Railway or Heroku

## Troubleshooting

### Database issues

If you get database errors, delete the database file and restart:
```bash
rm branchbot.db
uvicorn branchberg.app.main:app --reload
```

### Port already in use

If port 8000 or 8501 is busy:
```bash
# API on different port
uvicorn branchberg.app.main:app --port 8001

# Dashboard on different port
streamlit run branchberg/dashboard/streamlit_app.py --server.port 8502
```

### Can't connect to API from dashboard

Make sure the API_URL is set correctly:
```bash
export API_URL=http://localhost:8000
streamlit run branchberg/dashboard/streamlit_app.py
```

## Support

Questions? Email antonio.branch31@gmail.com or open an issue on GitHub.

Happy tracking! 💰
