# main.py
import asyncio
import logging
import time

import schedule

from app.bot import bot, dp
from app.periodic_tasks import start_hello_task

logging.basicConfig(level=logging.INFO)


def test_schedule():
    print("test schedule")


async def run_scheduler():
    schedule.every().sunday.at("23:59:59").do(test_schedule)
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


async def on_startup() -> None:
    asyncio.create_task(start_hello_task(bot))
    asyncio.create_task(run_scheduler())


async def main() -> None:
    """
    Main entry point for starting the bot.
    """
    print("Starting bot...")

    # Hook startup functionality
    dp.startup.register(on_startup)

    # Start polling updates
    await dp.start_polling(bot, skip_updates=True)

    schedule.every(3).seconds.do(test_schedule)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
