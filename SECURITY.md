# Security Policy

## 🔐 Security Best Practices

### Environment Variables & Secrets

**Never commit sensitive data to the repository:**
- API keys (OpenAI, Stripe, Gumroad, etc.)
- Database credentials 
- Webhook secrets
- Service account files
- SSL certificates

**Safe handling of secrets:**
1. **Use .env files locally** (never commit these)
2. **Use Railway environment variables** for production
3. **Rotate secrets regularly** (at least quarterly)
4. **Use SAFE_MODE=true** in development to disable external integrations

### 🔑 API Key Management

**Required Environment Variables:**
```bash
# Webhook secrets (from service providers)
STRIPE_WEBHOOK_SECRET=whsec_...    # From Stripe Dashboard
GUMROAD_WEBHOOK_SECRET=...         # Your shared secret

# AI & integrations (optional)
OPENAI_API_KEY=sk-...              # From OpenAI Dashboard
SLACK_WEBHOOK_URL=https://...      # From Slack App settings

# External services (optional)
NOTION_TOKEN=secret_...            # From Notion Integrations
GITHUB_TOKEN=ghp_...               # Personal access token
```

**Secret Rotation Schedule:**
- **Stripe webhook secrets**: When suspicious activity detected
- **OpenAI API keys**: Every 90 days
- **Notion tokens**: Every 6 months
- **GitHub tokens**: Every 6 months or when team changes

### 🛡️ Development Security

**Safe Mode Implementation:**
```python
# Always enable SAFE_MODE in development
SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() == "true"

if SAFE_MODE:
    # Disable external API calls
    # Use mock data
    # Skip webhook processing
```

**Local Development:**
1. Copy `.env.example` to `.env`
2. Set `SAFE_MODE=true` 
3. Only add real secrets when testing specific integrations
4. Never commit `.env` files

### 🔍 Webhook Security

**Stripe Webhooks:**
- Verify webhook signatures using `STRIPE_WEBHOOK_SECRET`
- Use HTTPS endpoints only
- Implement idempotency keys
- Log and monitor webhook attempts

**Gumroad Webhooks:**
- Validate signatures with shared secret
- Check seller_id matches expected values
- Sanitize all input data
- Rate limit webhook endpoints

### 📊 Database Security

**When using PostgreSQL:**
- Use connection pooling
- Enable SSL connections
- Implement proper user roles
- Regular backups with encryption
- Monitor for suspicious queries

### 🚨 Incident Response

**If a secret is compromised:**
1. **Immediate action**: Revoke the compromised key
2. **Generate new secret**: Create replacement immediately
3. **Update environment**: Deploy new secret to all environments
4. **Monitor impact**: Check logs for unauthorized usage
5. **Document**: Record incident and response actions

**Monitoring indicators:**
- Unexpected API usage
- Failed authentication attempts
- Unusual webhook traffic
- Database connection anomalies

### 🔧 Security Tools

**Code Security:**
- **ruff**: Catches basic security issues
- **pre-commit**: Prevents accidental commits of secrets
- **.gitignore**: Comprehensive exclusion of sensitive files

**Runtime Security:**
- **Environment isolation**: Use SAFE_MODE for development
- **Input validation**: Sanitize all webhook data
- **Error handling**: Don't expose internal details in errors

### 📋 Security Checklist

**Before Deployment:**
- [ ] All secrets removed from code
- [ ] Environment variables configured in Railway
- [ ] HTTPS enabled for all endpoints
- [ ] Webhook signature verification implemented
- [ ] Database SSL enabled
- [ ] Error pages don't expose internals
- [ ] Rate limiting configured
- [ ] Logging configured (without secrets)

**Regular Maintenance:**
- [ ] Review and rotate API keys quarterly
- [ ] Update dependencies monthly
- [ ] Review access logs monthly
- [ ] Test backup/restore procedures
- [ ] Verify webhook endpoint security
- [ ] Check for hardcoded secrets in code

### 🤝 Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. **Email**: antonio@abranch43.com with details
3. **Include**: Steps to reproduce, potential impact
4. **Expect**: Response within 48 hours
5. **Coordinate**: Responsible disclosure timeline

### 📚 Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Stripe Webhook Security](https://stripe.com/docs/webhooks/signatures)
- [Railway Security Best Practices](https://docs.railway.app/reference/variables)
- [Python Security Guidelines](https://python.org/dev/security/)

---
*Security is everyone's responsibility. When in doubt, choose the more secure option.*