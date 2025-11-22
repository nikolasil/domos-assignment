import asyncio
import logging
import json
import uuid
import os

from core.data_repository import DataRepository
from core.llm_client import LLMClient
from core.email.imap_reader import IMAPReader
from core.email.email_parser import parse_email
from core.email.smtp_sender import SMTPSender
from core.models import EmailMessage

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class PropertyManagerAi:
    def __init__(self, concurrency: int = 10):
        self.imap = IMAPReader()
        self.smtp = SMTPSender()
        self.data_repo = DataRepository()
        self.llm = LLMClient()
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)  # Limit parallel tasks

    async def run_once(self):
        """Fetch unread emails and process them asynchronously."""
        logger.info("Checking for unread emails...")
        try:
            async for raw_email in self.fetch_unread_stream():
                # Process each email concurrently but limited by semaphore
                asyncio.create_task(self.process_email(raw_email))
        except Exception as e:
            logger.error(f"Error in run_once: {e}")

    async def fetch_unread_stream(self):
        """Async generator yielding unread emails one by one."""
        try:
            async for raw in self.imap.fetch_unread_stream():  # async generator from IMAP
                yield raw
        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")

    async def process_email(self, raw_email: bytes):
        """Parse and reply to a single email."""
        async with self.semaphore:
            email_message = await self.safe_parse_email(raw_email)
            if email_message:
                await self.handle_email(email_message)

    @staticmethod
    async def safe_parse_email(raw: bytes) -> EmailMessage | None:
        try:
            # parsing is CPU-bound, can run in default executor
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, parse_email, raw)
        except Exception as e:
            logger.error(f"Failed to parse email: {e}")
            return None

    async def handle_email(self, email_message: EmailMessage):
        """Send reply asynchronously."""
        try:
            logger.info(f"Processing email from {email_message.sender}, subject: {email_message.subject}")

            context = self.data_repo.get_full_context_for_email(email_message.sender)

            logger.info(f"Context found: {context}")

            llm_response = self.llm.generate_response(
                email=email_message,
                context=context,
            )

            logger.info(f"LLM response: {llm_response}")

            # Produce action tickets
            if llm_response.action_items:
                os.makedirs("output", exist_ok=True)
                action_file = f"output/{uuid.uuid4()}.json"
                with open(action_file, "w", encoding="utf-8") as f:
                    json.dump(llm_response.action_items, f, indent=2)
                logger.info(f"Saved action items: {action_file}")


            # Send reply
            await self.smtp.send_email_async(
                to=email_message.sender,
                subject="Re: {}".format(email_message.subject),
                body=llm_response.reply,
            )

            logger.info(f"Sent reply to {email_message.sender}")
        except Exception as e:
            logger.error(f"Error handling email from {email_message.sender}: {e}")
