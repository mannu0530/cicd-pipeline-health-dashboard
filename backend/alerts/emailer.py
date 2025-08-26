
import os, smtplib
from email.message import EmailMessage

class EmailAlerter:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT","587"))
        self.user = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.email_from = os.getenv("EMAIL_FROM")
        self.email_to = os.getenv("EMAIL_TO")

    def notify(self, transition: dict):
        if not (self.host and self.user and self.password and self.email_from and self.email_to):
            return
        msg = EmailMessage()
        msg["Subject"] = f"[CI/CD] {transition.get('provider')} {transition.get('pipeline')} -> {transition.get('status_new')}"
        msg["From"] = self.email_from
        msg["To"] = self.email_to
        body = f"Pipeline: {transition.get('pipeline')}\nProvider: {transition.get('provider')}\nStatus: {transition.get('status_old')} -> {transition.get('status_new')}\nURL: {transition.get('web_url')}\nDuration: {transition.get('duration_seconds')}s\n"
        msg.set_content(body)
        with smtplib.SMTP(self.host, self.port) as s:
            s.starttls()
            s.login(self.user, self.password)
            s.send_message(msg)
