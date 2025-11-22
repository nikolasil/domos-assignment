import asyncio
from services.property_manager_ai import PropertyManagerAi

async def main():
    processor = PropertyManagerAi(concurrency=10)
    await processor.run_once()

if __name__ == "__main__":
    asyncio.run(main())