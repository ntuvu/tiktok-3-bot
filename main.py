# main.py
import asyncio

from bot import dp, bot, on_startup


async def main():
    print("Bot is running...")
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
