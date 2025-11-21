import imaplib
from config.settings import settings


class IMAPReader:
    def __init__(self):
        self.host = settings.IMAP_HOST
        self.user = settings.IMAP_USER
        self.password = settings.IMAP_PASSWORD

    def connect(self):
        mail = imaplib.IMAP4_SSL(self.host)
        mail.login(self.user, self.password)
        return mail

    def fetch_unread_emails(self) -> list[bytes]:
        """
        Returns a list of raw email bytes for each unread email.
        """
        try:
            mail = self.connect()
            mail.select("inbox")

            status, messages = mail.search(None, "(UNSEEN)")
            if status != "OK":
                return []

            email_ids = messages[0].split()

            raw_emails = []
            for eid in email_ids:
                _, data = mail.fetch(eid, "(RFC822)")
                raw_emails.append(data[0][1])

            return raw_emails

        except Exception as e:
            print(f"IMAP read error: {e}")
            return []
