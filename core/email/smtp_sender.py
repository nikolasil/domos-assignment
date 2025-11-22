import smtplib
from email.mime.text import MIMEText
import logging
import asyncio
from config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class SMTPSender:
    def __init__(self) -> None:
        self.host: str = settings.SMTP_HOST
        self.user: str = settings.SMTP_USER
        self.password: str = settings.SMTP_PASSWORD

    async def send_email_async(self, to: str, subject: str, body: str) -> None:
        """
        Sends an email asynchronously via SMTP_SSL using a thread pool.
        """
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._send_email_sync, to, subject, body)

    def _send_email_sync(self, to: str, subject: str, body: str) -> None:
        """
        Synchronous email sending logic (used internally by async wrapper).
        """
        msg = MIMEText(body)
        msg["From"] = self.user
        msg["To"] = to
        msg["Subject"] = subject

        try:
            logger.debug("Connecting to SMTP server %s", self.host)
            with smtplib.SMTP_SSL(self.host) as server:
                server.login(self.user, self.password)
                server.sendmail(self.user, [to], msg.as_string())
            logger.info("Sent email to %s with subject '%s'", to, subject)

        except smtplib.SMTPException as e:
            logger.error("SMTP send error to %s: %s", to, e)
        except Exception as e:
            logger.exception("Unexpected error while sending email to %s: %s", to, e)
