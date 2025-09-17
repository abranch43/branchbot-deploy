# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of branchbot-deploy seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do NOT create a public issue

Please do not report security vulnerabilities through public GitHub issues.

### 2. Report privately

Send a detailed report to **[antonio@branchingforty7.com](mailto:antonio@branchingforty7.com)** with:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if available)

### 3. Response timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix deployment:** Within 2 weeks (for critical vulnerabilities)

## Security Best Practices

### For Contributors

- **Never commit secrets:** Use environment variables for sensitive data
- **Validate all inputs:** Implement proper input validation and sanitization
- **Use HTTPS:** Ensure all external communications use HTTPS
- **Follow principle of least privilege:** Only request necessary permissions
- **Keep dependencies updated:** Regularly update requirements.txt

### For Users

#### Environment Security

1. **Secure your environment variables:**
   ```bash
   # Use strong, unique secrets
   STRIPE_WEBHOOK_SECRET=whsec_your_secure_secret_here
   GUMROAD_WEBHOOK_SECRET=your_unique_shared_secret
   ```

2. **Enable Railway security features:**
   - Use Railway's built-in environment variable encryption
   - Enable deployment protection
   - Monitor access logs

3. **Set SAFE_MODE in production:**
   ```bash
   SAFE_MODE=true  # Disables risky external integrations
   ```

#### Webhook Security

1. **Validate webhook signatures:**
   - Always verify Stripe webhook signatures
   - Implement HMAC validation for Gumroad webhooks

2. **Use HTTPS endpoints only:**
   ```
   ✅ https://your-api.railway.app/webhooks/stripe
   ❌ http://your-api.railway.app/webhooks/stripe
   ```

3. **Implement rate limiting:**
   - Monitor webhook frequency
   - Implement appropriate rate limits

#### Database Security

1. **Use connection encryption:**
   - Railway PostgreSQL uses SSL by default
   - Verify SSL connection in logs

2. **Limit database access:**
   - Use Railway's built-in database access controls
   - Monitor database connection logs

#### API Security

1. **Input validation:**
   - All webhook payloads are validated
   - Malformed requests are rejected

2. **Error handling:**
   - Sensitive information is not exposed in error messages
   - All errors are logged for monitoring

## Incident Response

### If you suspect a security breach:

1. **Immediate actions:**
   - Rotate all API keys and secrets
   - Check Railway deployment logs
   - Monitor webhook activity

2. **Contact us immediately:**
   - Email: antonio@branchingforty7.com
   - Include: timestamp, affected systems, suspected impact

3. **Documentation:**
   - Save relevant logs and evidence
   - Document timeline of events

## Automated Security

### GitHub Security Features

- **Dependabot:** Automated dependency updates enabled
- **Code scanning:** Automated vulnerability detection
- **Secret scanning:** Prevents accidental secret commits

### Railway Security Features

- **Environment encryption:** All environment variables encrypted at rest
- **HTTPS by default:** All deployments use HTTPS
- **Isolated environments:** Each deployment runs in isolation

## Security Updates

### Notification Methods

Security updates are communicated through:
- GitHub Security Advisories
- Repository releases with security tags
- Email notifications to contributors

### Update Process

1. Security patches are prioritized and fast-tracked
2. Emergency updates may bypass normal review process
3. All security updates include detailed change logs

## Compliance

### Data Protection

- **Minimal data collection:** Only necessary webhook data is processed
- **Data retention:** Events are retained according to business needs
- **Data encryption:** All data encrypted in transit and at rest

### Third-party Integrations

- **Stripe:** PCI DSS compliant payment processing
- **Gumroad:** Secure e-commerce platform integration
- **Railway:** SOC 2 Type II certified hosting

## Contact

For security-related questions or concerns:
- **Email:** antonio@branchingforty7.com
- **Response time:** Within 48 hours
- **Escalation:** Critical issues receive immediate attention

---

*This security policy is reviewed and updated regularly to ensure it reflects current best practices and threat landscape.*