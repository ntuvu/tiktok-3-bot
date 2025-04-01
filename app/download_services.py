import asyncio
import os

import aiofiles
import yt_dlp

from db_services import get_user_not_fetch


async def get_video_async(video_url: str) -> str:
    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)

    # yt-dlp options for downloading TikTok videos
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Download the best quality video with audio
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),  # Template for output file names
        'merge_output_format': 'mp4',  # Ensure the final merged file is MP4
    }

    # Run the download operation in a separate thread to avoid blocking
    loop = asyncio.get_event_loop()
    info_dict = await loop.run_in_executor(
        None,
        lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(video_url, download=True)
    )

    # Get the filename
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        video_file_path = ydl.prepare_filename(info_dict)  # Full path of the downloaded file

    return video_file_path


async def get_all_user_videos_async(user_url: str, username: str) -> list:
    if not ('@' in user_url or '/user/' in user_url):
        raise ValueError("The provided URL does not appear to be a valid TikTok user profile URL")

    # yt-dlp options for extracting video information without downloading
    ydl_opts = {
        'extract_flat': True,  # Don't download the videos, just get the info
        'quiet': True,  # Suppress output
        'dump_single_json': True,  # Get results as JSON
        'playlistend': 100,  # Limit number of videos to extract (adjust as needed)
        'ignoreerrors': True,  # Continue on errors
    }

    videos_info = []

    try:
        # Run the extraction in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(user_url, download=False)
        )

        if 'entries' in info:
            for entry in info['entries']:
                if entry:
                    videos_info.append({
                        'link': entry.get('url', ''),
                        'video_id': entry.get('id', ''),
                        'tiktok_user': username,
                    })
    except Exception as e:
        print(f"Error extracting videos: {str(e)}")

    return videos_info


async def create_csv(videos: list, filename: str = "tiktok_videos.csv") -> str:
    os.makedirs("output", exist_ok=True)
    file_path = os.path.join("output", filename)

    # Define headers
    headers = ["video_id", "link", "tiktok_user"]

    # Use aiofiles for async file operations
    async with aiofiles.open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        # We still need to use the synchronous csv writer, but the file operations are async
        # Write the file content as a string
        content = []
        content.append(','.join(headers))

        for video in videos:
            row = [
                str(video.get('video_id', '')),
                str(video.get('link', '')),
                str(video.get('tiktok_user', ''))
            ]
            content.append(','.join(row))

        await csvfile.write('\n'.join(content))

    return file_path


async def process():
    users = get_user_not_fetch()
    videos = []
    for user in users:
        video = await get_all_user_videos_async(user["link"], user["tiktok_user"])
        print(f'crawl user {user["tiktok_user"]} success')
        videos.extend(video)

    csv_path = await create_csv(videos)


asyncio.run(process())

# asyncio.run(get_all_user_videos_async("https://www.tiktok.com/@tamquandeoo23", "tamquandeoo23"))
