# app/bot.py
import io
import os

from aiogram import Bot, Dispatcher
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

from app.db_services import get_random_video, delete_video, inactive_video
from app.decoration import log_chat_id
from app.download_services import get_video_async

load_dotenv()

# Environmental variables
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
CHAT_ID: str = os.getenv("CHAT_ID", "")

user_router = Router()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Command handlers
@dp.message(Command("hello"))
@log_chat_id
async def handle_hello(message: Message) -> None:
    """Send a greeting."""
    await message.reply("Hello there! 👋")


@dp.message(Command("start"))
@log_chat_id
async def handle_start(message: Message) -> None:
    """Send a welcome message."""
    await message.reply("Welcome! Send /hello to get a greeting.")


@dp.message(Command("chatid"))
@log_chat_id
async def handle_chat_id(message: Message) -> None:
    """Send the current chat ID."""
    await message.reply(f"Your chat ID is: {message.chat.id}")


@dp.message(Command("download"))
@log_chat_id
async def handle_download(message: Message) -> None:
    """Download a video from a TikTok URL provided in the message."""
    video_url = message.text.split(" ", 1)[-1]  # Get the TikTok URL from the message

    if not video_url.startswith("http"):
        await message.reply("Please provide a valid TikTok URL.")
        return

    video_path = await get_video_async(video_url)
    try:
        await message.reply("Downloading your TikTok video... 📥")

        # Load video into memory with BytesIO
        with open(video_path, "rb") as video_file:
            video_data = io.BytesIO(video_file.read())
            video_data.seek(0)  # Reset buffer pointer to start of the file

        # Send the video using InputFile
        video_to_send = FSInputFile(video_path, filename="video.mp4")
        await bot.send_video(chat_id=message.chat.id, video=video_to_send)

    except Exception as e:
        await message.reply(f"An error occurred: {e}")

    finally:
        # Clean up: Close buffer and delete the local file
        if os.path.exists(video_path):
            os.remove(video_path)


@dp.message(Command("random"))
@log_chat_id
async def get_random_video_command(message: Message) -> None:
    video_url = get_random_video()
    if not video_url:
        await message.reply("No video found.")
        return

    video_path = await get_video_async(video_url)
    try:
        # Notify the user that the bot is uploading the video
        await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")

        # Load video into memory with BytesIO
        with open(video_path, "rb") as video_file:
            video_data = io.BytesIO(video_file.read())
            video_data.seek(0)  # Reset buffer pointer to start of the file

        # Send the video using InputFile
        video_to_send = FSInputFile(video_path, filename="video.mp4")
        await bot.send_video(chat_id=message.chat.id, video=video_to_send, caption=f"{video_url}")
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


@dp.message(Command("delete"))
@log_chat_id
async def delete_video_command(message: Message) -> None:
    video_url = message.text.split(" ", 1)[-1]
    if not video_url:
        await message.reply("Please provide a valid TikTok URL.")
        return

    try:
        delete_video(video_url)
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
    finally:
        await message.reply("Video deleted.")


@dp.message(Command("inactive"))
@log_chat_id
async def delete_video_command(message: Message) -> None:
    video_url = message.text.split(" ", 1)[-1]
    if not video_url:
        await message.reply("Please provide a valid TikTok URL.")
        return

    try:
        inactive_video(video_url)
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
    finally:
        await message.reply("Video inactive.")
