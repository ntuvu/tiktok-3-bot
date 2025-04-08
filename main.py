import asyncio
import logging
import os

import schedule
from flask import Flask

from app.bot import bot, dp
from app.download_services import process_10
from app.periodic_tasks import start_hello_task

app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running!"


def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


logging.basicConfig(level=logging.INFO)


def schedule_handler():
    asyncio.create_task(process_10())


async def run_scheduler():
    schedule.every().sunday.at("23:59:59").do(schedule_handler)
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


async def on_startup() -> None:
    asyncio.create_task(start_hello_task(bot))
    asyncio.create_task(run_scheduler())


async def main() -> None:
    print("Starting bot...")

    # Hook startup functionality
    dp.startup.register(on_startup)

    # Start monitoring memory usage as an asyncio task
    # start_memory_monitor(interval=5)

    # Start polling updates
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
