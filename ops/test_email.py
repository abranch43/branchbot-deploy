import os
import smtplib
from email.mime.text import MIMEText


def send():
    host = os.getenv("SMTP_HOST")
    user = os.getenv("SMTP_USER")
    pw = os.getenv("SMTP_PASS")
    to = [e.strip() for e in os.getenv("ALERT_TO", "").split(",") if e.strip()]
    from_ = os.getenv("ALERT_FROM")
    if not (host and user and pw and to and from_):
        print("Missing SMTP or recipient envs; set .env first.")
        return 1
    msg = MIMEText("BranchBot test email OK.")
    msg["Subject"] = "BranchBot: test email"
    msg["From"] = from_
    msg["To"] = ", ".join(to)
    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as s:
        s.starttls()
        s.login(user, pw)
        s.sendmail(from_, to, msg.as_string())
    print("Test email sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(send())
