import imaplib
import asyncio
from typing import AsyncGenerator, Optional
import logging
from config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class IMAPReader:
    def __init__(self):
        self.host: str = settings.IMAP_HOST
        self.user: str = settings.IMAP_USER
        self.password: str = settings.IMAP_PASSWORD

    def _connect_sync(self) -> imaplib.IMAP4_SSL:
        """Synchronous connection to IMAP server."""
        logger.debug("Connecting to IMAP server %s", self.host)
        mail = imaplib.IMAP4_SSL(self.host)
        mail.login(self.user, self.password)
        logger.info("Logged in as %s", self.user)
        return mail

    async def fetch_unread_stream(self) -> AsyncGenerator[bytes, None]:
        """
        Async generator yielding unread emails one by one.
        Uses a thread pool internally to avoid blocking the event loop.
        """
        loop = asyncio.get_running_loop()
        mail: imaplib.IMAP4_SSL = await loop.run_in_executor(None, self._connect_sync)

        try:
            mail.select("inbox")
            status, messages_raw = await loop.run_in_executor(None, mail.search, None, "(UNSEEN)")

            if status != "OK" or not messages_raw or not messages_raw[0]:
                logger.info("No unread emails found.")
                return

            email_ids = [eid.decode("utf-8") for eid in messages_raw[0].split()]
            logger.info("Found %d unread emails.", len(email_ids))

            for eid in email_ids:
                fetch_status, fetch_data = await loop.run_in_executor(None, mail.fetch, eid, "(RFC822)")
                if fetch_status != "OK" or not fetch_data:
                    logger.warning("Failed to fetch email ID %s", eid)
                    continue

                # Extract raw email payload
                for item in fetch_data:
                    if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], (bytes, type(None))):
                        payload: Optional[bytes] = item[1]
                        if payload is not None:
                            yield payload

        except imaplib.IMAP4.error as e:
            logger.error("IMAP error: %s", e)
        except Exception as e:
            logger.exception("Unexpected error while fetching emails: %s", e)
        finally:
            await loop.run_in_executor(None, mail.logout)
            logger.info("Logged out from IMAP server.")
