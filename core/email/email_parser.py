import email
from email.message import Message
from email.header import decode_header
from typing import Tuple, Optional
from core.models import EmailMessage


def decode_header_value(value: str) -> str:
    """
    Decodes an email header value into a UTF-8 string.
    """
    decoded_parts: list[Tuple[bytes | str, Optional[str]]] = decode_header(value)
    result: str = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="ignore")
        else:
            result += part
    return result


def extract_body(message: Message) -> str:
    """
    Extracts the plain text body from an email message in a type-safe way.
    """
    if message.is_multipart():
        for part in message.walk():
            content_type: str = part.get_content_type()
            content_disposition: str = str(part.get("Content-Disposition", ""))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    return payload.decode("utf-8", errors="ignore")
        return ""
    else:
        payload = message.get_payload(decode=True)
        if isinstance(payload, bytes):
            return payload.decode("utf-8", errors="ignore")
        elif isinstance(payload, str):
            return payload  # already a string
        else:
            return ""  # fallback if None or unknown type


def parse_email(raw_email_bytes: bytes) -> EmailMessage:
    """
    Parses raw email bytes into an EmailMessage object.
    """
    msg: Message = email.message_from_bytes(raw_email_bytes)

    subject: str = decode_header_value(msg.get("Subject", "") or "")
    sender: str = decode_header_value(msg.get("From", "") or "")
    body: str = extract_body(msg)

    return EmailMessage(
        subject=subject.strip(),
        body=body.strip(),
        sender=sender.strip(),
    )
