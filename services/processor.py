from typing import List
from email_client.imap_reader import IMAPReader
from email_client.email_parser import parse_email
from email_client.smtp_sender import SMTPSender
from core.models import EmailMessage


class EmailProcessor:
    def __init__(self) -> None:
        self.imap: IMAPReader = IMAPReader()
        self.smtp: SMTPSender = SMTPSender()

    def run_once(self) -> None:
        print("Checking for unread emails...")

        raw_emails: List[bytes] = self.imap.fetch_unread_emails()
        if not raw_emails:
            print("No unread emails.")
            return

        for raw in raw_emails:
            email_message: EmailMessage = parse_email(raw)
            print("Parsed:", email_message)

            # Temporary test reply
            reply_text: str = (
                f"Hello,\n\nWe received your message:\n'{email_message.body}'\n\nThank you."
            )

            # Basic echo reply
            self.smtp.send_email(
                to=email_message.sender,
                subject=f"Re: {email_message.subject}",
                body=reply_text,
            )
