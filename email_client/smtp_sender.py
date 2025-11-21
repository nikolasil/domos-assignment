import smtplib
from email.mime.text import MIMEText
from config.settings import settings


class SMTPSender:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD

    def send_email(self, to: str, subject: str, body: str):
        msg = MIMEText(body)
        msg["From"] = self.user
        msg["To"] = to
        msg["Subject"] = subject

        try:
            with smtplib.SMTP_SSL(self.host) as server:
                server.login(self.user, self.password)
                server.sendmail(self.user, [to], msg.as_string())
            print(f"Sent email to {to}")
        except Exception as e:
            print(f"SMTP send error: {e}")
