import imaplib
from typing import List, Optional
from config.settings import settings


class IMAPReader:
    def __init__(self) -> None:
        self.host: str = settings.IMAP_HOST
        self.user: str = settings.IMAP_USER
        self.password: str = settings.IMAP_PASSWORD

    def connect(self) -> imaplib.IMAP4_SSL:
        """
        Connects and logs in to the IMAP server.
        """
        mail: imaplib.IMAP4_SSL = imaplib.IMAP4_SSL(self.host)
        mail.login(self.user, self.password)
        return mail

    def fetch_unread_emails(self) -> List[bytes]:
        """
        Returns a list of raw email bytes for each unread email.
        """
        try:
            mail: imaplib.IMAP4_SSL = self.connect()
            mail.select("inbox")

            status: str
            messages_raw: List[bytes]
            status, messages_raw = mail.search(None, "(UNSEEN)")
            if status != "OK" or not messages_raw:
                return []

            email_ids: List[str] = [eid.decode("utf-8") for eid in messages_raw[0].split()]

            raw_emails: List[bytes] = []

            for eid in email_ids:
                fetch_status, fetch_data = mail.fetch(eid, "(RFC822)")
                if fetch_status != "OK" or not fetch_data:
                    continue

                # filter out only tuples with payload
                for item in fetch_data:
                    if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], (bytes, type(None))):
                        payload: Optional[bytes] = item[1]
                        if payload is not None:
                            raw_emails.append(payload)


            return raw_emails

        except imaplib.IMAP4.error as e:
            print(f"IMAP error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
