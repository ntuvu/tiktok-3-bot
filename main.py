# main.py
import asyncio
import logging

from app.bot import bot, dp
from app.periodic_tasks import start_hello_task


async def on_startup() -> None:
    """
    Startup logic for the bot, including periodic task initialization.
    """
    # Start periodic tasks like sending weekly messages
    asyncio.create_task(start_hello_task(bot))


async def main() -> None:
    """
    Main entry point for starting the bot.
    """
    print("Starting bot...")
    logging.basicConfig(level=logging.INFO)

    # Hook startup functionality
    dp.startup.register(on_startup)

    # Start polling updates
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
