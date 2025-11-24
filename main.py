import asyncio
import logging
from services.property_manager_ai import PropertyManagerAi

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


async def main():
    processor = PropertyManagerAi(concurrency=2, polling=2, max_retries=2, unread_days_back=1)
    logger.info("Starting async email property manager assistant...")

    while True:
        try:
            await processor.run_once()
        except Exception as e:
            logger.error("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
