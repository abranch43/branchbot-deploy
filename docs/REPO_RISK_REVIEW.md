# Repository Risk Review (Security, Stability, Maintainability)

## High-priority findings

1. **PO over-billing risk** (fixed): invoices could previously be created without enforcing cumulative invoice totals against PO amount.
   - **Fix implemented:** non-void invoices are now capped so cumulative invoice amount cannot exceed PO amount.
2. **Duplicate payment race risk** (fixed): duplicate payment attempts could slip through across concurrent requests.
   - **Fix implemented:** service-layer duplicate checks plus database uniqueness on `payments.invoice_id`.
3. **Weak lifecycle isolation in a large app module** (fixed): operational and domain logic were tightly coupled in `main.py`, increasing defect risk.
   - **Fix implemented:** split into dedicated routes, schemas, and services for cleaner separation.

## Medium-priority findings

1. **Broad CORS policy** (`allow_origins=["*"]`): permissive defaults increase exposure in production.
   - **Suggestion:** lock CORS to approved domains through environment-based configuration.
2. **SQLAlchemy 2.x deprecation warnings** (`declarative_base` import path): potential future breakage.
   - **Suggestion:** migrate to `sqlalchemy.orm.declarative_base`.
3. **Deprecated FastAPI HTTP status constants in internals/tests output**.
   - **Suggestion:** replace with `HTTP_422_UNPROCESSABLE_CONTENT` and align tests.

## Stability summary

- Webhook tests and PO/payment tests pass after refactor.
- New tests explicitly cover invoice-over-PO blocking and duplicate-payment blocking.
