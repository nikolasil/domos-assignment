import email
from email.header import decode_header
from core.models import EmailMessage


def decode_header_value(value: str) -> str:
    decoded_parts = decode_header(value)
    result = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="ignore")
        else:
            result += part
    return result


def extract_body(message) -> str:
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode("utf-8", errors="ignore")
        return ""
    else:
        return message.get_payload(decode=True).decode("utf-8", errors="ignore")


def parse_email(raw_email_bytes: bytes) -> EmailMessage:
    msg = email.message_from_bytes(raw_email_bytes)

    subject = decode_header_value(msg.get("Subject", ""))
    sender = decode_header_value(msg.get("From", ""))
    body = extract_body(msg)

    return EmailMessage(
        subject=subject.strip(),
        body=body.strip(),
        sender=sender.strip(),
    )
