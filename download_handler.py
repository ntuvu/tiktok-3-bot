# tiktok_downloader.py

import asyncio
from typing import Union, Any, Coroutine

import aiohttp

from db import get_video_link

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def extract_tiktok_video_id(url: str) -> str | None:
    parts = url.split('/')

    for part in parts:
        if 'video' in part:
            video_id = parts[parts.index(part) + 1]
            return video_id

    if '?' in url:
        base_url = url.split('?')[0]
        parts = base_url.split('/')
        for part in reversed(parts):
            if part:
                return part

    return None


async def fetch_tiktok_video(video_id: str) -> tuple[bool, Union[str, tuple[bytes, str]]]:
    video_url = f'https://tikcdn.io/ssstik/{video_id}'
    print('video_url', video_url)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url, timeout=300) as resp:
                if resp.status != 200:
                    return False, f"Failed to download video: HTTP {resp.status}"

                content_length = int(resp.headers.get('Content-Length', 0))
                if content_length > MAX_FILE_SIZE:
                    return False, "Video exceeds the 20MB file size limit."

                content = await resp.read()
                return True, (content, video_id)

    except aiohttp.ClientError as e:
        return False, f"Network error: {str(e)}"
    except asyncio.TimeoutError:
        return False, "Request timed out. Please try again later."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


async def get_tiktok_video(url: str) -> tuple[bool, Union[str, tuple[bytes, str]]]:
    video_id = extract_tiktok_video_id(url)
    if not video_id:
        return False, "Failed to extract video ID from URL."
    return await fetch_tiktok_video(video_id)


async def send_video() -> tuple[bool, str] | tuple[bool, bytes]:
    video_link = get_video_link()
    if not video_link:
        return False, "Failed to get video_id from DB."

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_link, timeout=30000) as resp:
                if resp.status != 200:
                    return False, f"Failed to download video: HTTP {resp.status}"

                content_length = int(resp.headers.get('Content-Length', 0))
                if content_length > MAX_FILE_SIZE:
                    return False, "Video exceeds the 20MB file size limit."

                content = await resp.read()
                return True, content

    except aiohttp.ClientError as e:
        return False, f"Network error: {str(e)}"
    except asyncio.TimeoutError:
        return False, "Request timed out. Please try again later."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
