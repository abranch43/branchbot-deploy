# Proof Checklist

Use this checklist before claiming the repository is fully production-ready.

## Identity and Documentation

- [ ] README reflects the actual deploy path in use
- [ ] Product naming is consistent across repo, dashboard, and API
- [ ] Current working capabilities are listed clearly
- [ ] Unproven capabilities are not overstated

## Runtime Validation

- [ ] API boots successfully
- [ ] Dashboard boots successfully
- [ ] API and dashboard connect correctly
- [ ] Database connection is successful
- [ ] `/health` responds with status OK
- [ ] `/version` returns a real version and commit context

## Workflow Validation

- [ ] Manual transaction ingest works end to end
- [ ] CSV ingest works end to end
- [ ] Revenue summary reflects ingested data
- [ ] Revenue events endpoint returns expected records
- [ ] Purchase order creation works
- [ ] Invoice creation works
- [ ] Payment recording works
- [ ] Audit log entries are created correctly

## Webhook Validation

- [ ] Stripe webhook verification is validated with live or test events
- [ ] Gumroad webhook verification is validated with live or test events
- [ ] Invalid signatures are rejected appropriately

## Delivery Confidence

- [ ] CI fails loudly on real regressions
- [ ] Key environment variables are documented in one place
- [ ] Local development instructions match actual startup commands
- [ ] Production deployment instructions match actual platform behavior
