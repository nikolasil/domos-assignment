from email_client.imap_reader import IMAPReader
from email_client.email_parser import parse_email
from email_client.smtp_sender import SMTPSender


class EmailProcessor:
    def __init__(self):
        self.imap = IMAPReader()
        self.smtp = SMTPSender()

    def run_once(self):
        print("Checking for unread emails...")

        raw_emails = self.imap.fetch_unread_emails()
        if not raw_emails:
            print("No unread emails.")
            return

        for raw in raw_emails:
            email_message = parse_email(raw)
            print("Parsed:", email_message)

            # temporary test reply
            reply_text = f"Hello,\n\nWe received your message:\n'{email_message.body}'\n\nThank you."

            # basic echo reply
            self.smtp.send_email(
                to=email_message.sender,
                subject=f"Re: {email_message.subject}",
                body=reply_text,
            )
