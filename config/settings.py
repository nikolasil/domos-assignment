import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    IMAP_HOST: str = os.getenv("IMAP_HOST", "")
    IMAP_USER: str = os.getenv("IMAP_USER", "")
    IMAP_PASSWORD: str = os.getenv("IMAP_PASSWORD", "")
    
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

settings = Settings()
