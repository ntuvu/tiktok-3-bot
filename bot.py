# bot.py
import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from dotenv import load_dotenv

from download_handler import get_tiktok_video, send_video

load_dotenv()

# Replace with your bot token
BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
CHAT_ID: str = os.getenv('CHAT_ID', '')

ONE_WEEK = 7 * 24 * 60 * 60  # 604800 seconds

# Create bot and dispatcher
bot: Bot = Bot(token=BOT_TOKEN)
dp: Dispatcher = Dispatcher()


# /hello command handler
@dp.message(Command("hello"))
async def send_hello(message: Message) -> None:
    await message.reply("Hello there! 👋")


# /start command handler
@dp.message(Command("start"))
async def send_welcome(message: Message) -> None:
    await message.reply("Welcome! Send /hello to get a greeting.")


@dp.message(Command("get"))
async def get_command(message: Message) -> None:
    """
    Handler for the /get command to download and send TikTok videos.

    Args:
        message: The message containing the command
    """
    # Extract URL from command
    url: str = message.text.replace("/get", "", 1).strip()

    # Validate URL
    if 'tiktok.com' not in url:
        await message.reply("Please send a valid TikTok link.")
        return

    await message.reply("⏳ Downloading, please wait...")

    try:
        # Get video from the downloader module
        success: bool
        result: tuple | str
        success, result = await get_tiktok_video(url)

        if success:
            # Unpack the result
            content: bytes
            video_id: str
            content, video_id = result

            # Create BufferedInputFile
            video: BufferedInputFile = BufferedInputFile(content, filename=f"tiktok_{video_id}.mp4")

            # Send video directly without saving to disk
            await message.reply_video(video=video)
        else:
            # If download failed, send error message
            await message.reply(f"❌ {result}")

    except Exception as e:
        await message.reply(f"❌ Error: {e}")


@dp.message(Command("chatid"))
async def send_chat_id(message: Message) -> None:
    """
    Handler for the /chatid command to send the user's chat ID.

    Args:
        message: The message instance
    """
    chat_id = message.chat.id
    await message.reply(f"Your chat ID is: {chat_id}")


@dp.message(Command("x"))
async def send_video_command(message: Message) -> None:
    await message.reply("⏳ Downloading, please wait...")

    try:
        # Get video from the downloader module
        success: bool
        result: str | bytes
        success, result = await send_video()

        if success:
            current_timestamp: str = datetime.now().strftime("%Y%m%d%H%M%S")
            content: bytes = result
            video: BufferedInputFile = BufferedInputFile(content, filename=f"tiktok_{current_timestamp}.mp4")
            await message.reply_video(video = video)
        else:
            # If download failed, send error message
            await message.reply(f"❌ {result}")

    except Exception as e:
        await message.reply(f"❌ Error: {e}")


async def send_hello_message():
    """Send a hello message every 10 seconds"""
    while True:
        try:
            await bot.send_message(CHAT_ID, "Hello!")
        except Exception as e:
            await bot.send_message(CHAT_ID, f'Error: {str(e)}')

        # Wait for 10 seconds before sending the next message
        await asyncio.sleep(ONE_WEEK)


async def on_startup() -> None:
    """Start the periodic message sender when the bot starts"""
    asyncio.create_task(send_hello_message())
