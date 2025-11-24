import logging
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional

from aioimaplib import IMAP4_SSL
from config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


def is_ok_response(response) -> bool:
    """Check if aioimaplib response indicates success."""
    if not response.lines:
        return False
    return any(line.startswith(b"OK") or b"Success" in line for line in response.lines)


class IMAPReader:
    def __init__(self, days_back: int = 1):
        self.host: str = settings.IMAP_HOST
        self.user: str = settings.IMAP_USER
        self.password: str = settings.IMAP_PASSWORD
        self.days_back = days_back

    async def fetch_unread_stream(self) -> AsyncGenerator[bytes, None]:
        """
        Fully async IMAP email fetcher using aioimaplib.
        Streams unread emails from the last N days.
        """
        imap = IMAP4_SSL(self.host)
        try:
            # Connect and wait for server greeting
            await imap.wait_hello_from_server()
            await imap.login(self.user, self.password)
            logger.info(f"Logged in to IMAP as {self.user}")

            # Select INBOX
            select_result = await imap.select("INBOX")
            if not is_ok_response(select_result):
                logger.error("Failed to select INBOX")
                return

            # Build search query
            since_date = (datetime.now() - timedelta(days=self.days_back)).strftime("%d-%b-%Y")
            search_criteria = f'(UNSEEN SINCE {since_date})'

            # Search for unread messages
            search_result = await imap.search(search_criteria)
            if not is_ok_response(search_result) or not search_result.lines:
                logger.info("No unread emails found.")
                return

            # Extract message IDs as strings from first line only
            message_ids = [
                msg_id.decode() for msg_id in search_result.lines[0].split() if msg_id.isdigit()
            ]
            logger.info(f"Found {len(message_ids)} unread emails.")

            # Fetch each email
            for msg_id in message_ids:
                fetch_result = await imap.fetch(msg_id, "RFC822")
                if not is_ok_response(fetch_result) or not fetch_result.lines:
                    logger.warning(f"Failed to fetch message ID {msg_id}")
                    continue

                # Extract raw email bytes from lines (usually lines[1] has the email body)
                raw_email: Optional[bytes] = fetch_result.lines[1] if len(fetch_result.lines) > 1 else fetch_result.lines[0]

                if raw_email:
                    yield raw_email

        except Exception as e:
            logger.exception(f"IMAP error: {e}")

        finally:
            await imap.logout()
            logger.info("Logged out from IMAP.")
