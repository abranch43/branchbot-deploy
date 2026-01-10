# Universal Income Ingest - Feature Documentation

## Overview

The Universal Income Ingest feature provides a comprehensive solution for tracking all revenue streams in BranchOS through a FastAPI backend and Streamlit dashboard.

## Features

### FastAPI Backend

The backend provides REST API endpoints for revenue tracking:

- **POST /ingest/manual** - Add individual manual transactions
- **POST /ingest/csv** - Bulk upload transactions from CSV files with column mapping
- **GET /revenue/summary** - Get total revenue and transaction count
- **GET /revenue/events** - Retrieve recent transactions with pagination

### Streamlit Dashboard

The dashboard provides a user-friendly interface with three pages:

1. **Income Ingest** - Add transactions manually or via CSV upload
2. **Revenue Summary** - View key metrics (total revenue, transaction count, average)
3. **Transaction History** - Browse all transactions with filtering

### Database

- SQLAlchemy-based ORM with support for PostgreSQL and SQLite
- Auto-creates tables on startup
- Revenue events table with full transaction metadata

## Installation

### Requirements

```bash
pip install -r requirements.txt
```

New dependencies added:
- sqlalchemy>=2.0 - ORM for database operations
- psycopg2-binary>=2.9 - PostgreSQL adapter
- pandas>=2.0 - CSV processing
- python-multipart>=0.0.6 - File upload support

### Environment Variables

Add to your `.env` file:

```bash
DATABASE_URL=postgresql://user:pass@localhost/branchbot
# Or for SQLite (development):
# DATABASE_URL=sqlite:///./branchbot.db
```

## Usage

### Starting the API Server

```bash
uvicorn branchberg.app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Starting the Streamlit Dashboard

```bash
# Set the API URL
export API_URL=http://localhost:8000

# Start Streamlit
streamlit run branchberg/dashboard/streamlit_app.py
```

The dashboard will be available at `http://localhost:8501`

### API Examples

#### Add Manual Transaction

```bash
curl -X POST http://localhost:8000/ingest/manual \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150.50,
    "currency": "USD",
    "customer_email": "customer@example.com",
    "entity": "A+ Enterprise LLC",
    "description": "Consulting services"
  }'
```

#### Upload CSV

```bash
curl -X POST http://localhost:8000/ingest/csv \
  -F "file=@transactions.csv" \
  -F "amount_column=amount" \
  -F "email_column=email" \
  -F "entity_column=entity"
```

CSV format example:
```csv
amount,email,entity
100.50,user1@test.com,A+ Enterprise LLC
200.75,user2@test.com,Legacy Unchained Inc
```

#### Get Revenue Summary

```bash
curl http://localhost:8000/revenue/summary
```

Response:
```json
{
  "total_cents": 57675,
  "total_dollars": 576.75,
  "count": 4,
  "currency": "USD"
}
```

#### Get Recent Transactions

```bash
curl http://localhost:8000/revenue/events?limit=10
```

## Database Schema

### revenue_events Table

| Column | Type | Description |
|--------|------|-------------|
| id | String (UUID) | Primary key |
| event_id | String | Unique event identifier |
| provider | String | Provider type: stripe, gumroad, manual |
| event_type | String | Event type: manual_entry, csv_import, etc. |
| amount_cents | Integer | Amount in cents |
| currency | String | ISO 4217 currency code (default: USD) |
| customer_email | String | Customer email (optional) |
| customer_id | String | Customer ID (optional) |
| event_metadata | JSON | Additional metadata |
| created_at | DateTime | Creation timestamp |
| processed_at | DateTime | Processing timestamp |
| entity | String | Business entity (optional) |

## Testing

### Run Manual Tests

A comprehensive test script is provided:

```bash
python test_income_ingest_manual.py
```

This runs:
- Root endpoint test
- Manual transaction creation
- Revenue summary calculation
- Event retrieval and ordering
- CSV upload functionality

All tests use isolated SQLite databases and clean up after themselves.

### Pytest Tests

Standard pytest tests are available in `tests/branchberg/`:

```bash
pytest tests/branchberg/test_income_ingest.py -v
```

## Production Deployment

### Railway/Heroku

The application is ready for deployment on Railway or Heroku:

1. Set `DATABASE_URL` environment variable
2. The application auto-creates tables on startup
3. Use the Procfile for automatic deployment

### Security Considerations

- Always use HTTPS in production
- Set strong DATABASE_URL credentials
- Implement authentication for write endpoints in production
- Validate all input data
- Use environment variables for secrets

## Future Enhancements

The following features are documented in AGENTS.md for future implementation:

- Stripe webhook integration
- Gumroad webhook integration
- Webhook signature verification
- Daily/weekly revenue summaries
- Anomaly detection
- Slack/email notifications
- Revenue forecasting

## Architecture

```
branchberg/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI application
│   └── database.py     # SQLAlchemy models
└── dashboard/
    └── streamlit_app.py  # Streamlit dashboard

tests/
└── branchberg/
    ├── __init__.py
    ├── conftest.py
    └── test_income_ingest.py
```

## Support

For issues or questions:
- Maintainer: Antonio Branch (antonio.branch31@gmail.com)
- Repository: https://github.com/abranch43/branchbot-deploy

## License

See LICENSE file in repository root.
