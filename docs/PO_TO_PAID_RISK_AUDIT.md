# PO-to-Paid Flow Audit — Cash Flow Risk Review

Date: 2026-03-03
Scope: `branchberg/app/main.py` PO → Invoice → Payment endpoints and related models/tests.

## Priority 1 (High)

### 1) Payment method has no validation (can accept empty/invalid values)
**Why this matters:** Invalid payment methods reduce traceability for collections and reconciliation, making disputed or delayed collections harder to resolve.

**Evidence**
- `PaymentCreate.method` is required as a string, but no allowed-value validation exists in `record_payment`. (`/invoice/{invoice_id}/payment`)

**Minimal fix**
- Enforce an allowlist in API validation (`ach`, `wire`, `check`, `card`, `other`) and reject blank values.
- Add a unit test for invalid/blank method.

---

### 2) Currency mismatch is not checked across PO, invoice, and payment
**Why this matters:** A PO in one currency can be invoiced/paid in another without rejection, creating silent under/over collection risk and incorrect revenue rollups.

**Evidence**
- `create_invoice` does not validate `payload.currency` against `purchase_order.currency`.
- `record_payment` does not validate `payload.currency` against `invoice.currency` or `purchase_order.currency`.

**Minimal fix**
- Reject invoice creation when invoice currency differs from PO currency.
- Reject payment creation when payment currency differs from invoice/PO currency.
- Add tests for mismatched currency failures.

---

### 3) Overpayments are accepted and posted as revenue without explicit handling
**Why this matters:** `record_payment` only checks `amount >= invoice amount`, then books full payment to revenue. Overpayments can overstate realized revenue if credits/refunds are expected later.

**Evidence**
- `record_payment` validates only lower bound (`amount_cents < invoice.amount_cents`), then inserts revenue event for full payment amount.

**Minimal fix**
- Require exact match by default, or support overpayment with explicit `metadata.overpayment_reason` + separate unapplied credit accounting.
- Add tests for overpayment behavior.

## Priority 2 (Medium)

### 4) No due-date / aging workflow hooks for collections follow-up
**Why this matters:** Invoices can be created without `due_at` and no follow-up tasks/alerts are emitted when past due, increasing risk of late payment.

**Evidence**
- `InvoiceCreate.due_at` is optional.
- No overdue monitoring endpoint/job/notification in PO flow code.

**Minimal fix**
- Require `due_at` for `sent` invoices (or set policy default net terms).
- Add scheduled overdue detector + warning notifications (Slack/email).

---

### 5) No operational notifications on critical state transitions/failures
**Why this matters:** PO/invoice/payment events are persisted to `audit_log`, but no proactive notification on failed payment postings, duplicate references, or unusual conditions.

**Evidence**
- `_record_audit_log` writes entries, but no notifier integration in PO/invoice/payment handlers.

**Minimal fix**
- Add lightweight notifier hook for:
  - Payment POST 4xx/5xx on collection attempts
  - Duplicate payment/invoice conflicts
  - Invoices aging beyond SLA

---

### 6) API allows any actor string; weak accountability controls
**Why this matters:** `actor` defaults to `system` and is user-supplied without auth context. This weakens attribution and slows incident response when revenue events are disputed.

**Evidence**
- `actor` is optional in create endpoints and defaults to `system`.

**Minimal fix**
- Source actor from authenticated principal instead of payload.
- Keep optional free-text `reason`, but lock actor to auth identity.

## Priority 3 (Low)

### 7) Webhook revenue paths are placeholders (external cash events can be missed)
**Why this matters:** Stripe/Gumroad webhook endpoints are not implemented. Revenue dependent on webhooks can be delayed/lost unless entered manually.

**Evidence**
- `/webhooks/stripe` and `/webhooks/gumroad` return `not_implemented`.

**Minimal fix**
- Implement signature verification, idempotency keyed by provider event ID, and dead-letter/retry logging.
- Add alerting for webhook processing failures.

---

### 8) Limited negative-path test coverage for cash-collection edge cases
**Why this matters:** Existing tests cover entity presence and required payment artifact, but not currency mismatch, overpayment policy, invalid method, or duplicate handling at API layer.

**Evidence**
- `tests/branchberg/test_po_flow.py` currently focuses on entity/artifact invariants.

**Minimal fix**
- Add focused tests for each edge case above.

## Quick Wins (1–2 sprint days)
1. Add validation guards for currency + payment method.
2. Enforce exact-match payment amount (or explicit overpayment pathway).
3. Require `due_at` for sent invoices; add basic overdue query endpoint.
4. Emit notifications for failed/duplicate payment attempts.
5. Expand unit tests for payment/invoice edge conditions.
