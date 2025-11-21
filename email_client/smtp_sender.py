import smtplib
from email.mime.text import MIMEText
from config.settings import settings


class SMTPSender:
    def __init__(self) -> None:
        self.host: str = settings.SMTP_HOST
        self.user: str = settings.SMTP_USER
        self.password: str = settings.SMTP_PASSWORD

    def send_email(self, to: str, subject: str, body: str) -> None:
        """
        Sends an email via SMTP_SSL.
        """
        msg: MIMEText = MIMEText(body)
        msg["From"] = self.user
        msg["To"] = to
        msg["Subject"] = subject

        try:
            with smtplib.SMTP_SSL(self.host) as server:
                server.login(self.user, self.password)
                server.sendmail(self.user, [to], msg.as_string())
            print(f"Sent email to {to}")
        except smtplib.SMTPException as e:
            # More specific than generic Exception
            print(f"SMTP send error: {e}")
        except Exception as e:
            # fallback for unexpected errors
            print(f"Unexpected error: {e}")
