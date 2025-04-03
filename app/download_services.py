import asyncio
import os

import aiofiles
import yt_dlp

from app.db_services import get_user_not_fetch, get_user_fetched

YT_DLP_DEFAULT_OPTS = {
    'extract_flat': True,  # Don't download the videos, just get the info
    'quiet': True,  # Suppress output
    'dump_single_json': True,  # Get results as JSON
    'ignoreerrors': True,  # Continue on errors
}

DOWNLOAD_DIR = "downloads"


def get_yt_dlp_options():
    """ Returns yt-dlp options for TikTok video downloads. """
    return {
        'format': 'bestvideo+bestaudio/best',  # Download the best quality video with audio
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),  # Template for output file names
        'merge_output_format': 'mp4',  # Ensure the final merged file is MP4
    }


async def get_video_async(video_url: str) -> str:
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # Ensure download_dir exists
    ydl_opts = get_yt_dlp_options()
    loop = asyncio.get_event_loop()

    print("before download")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Run yt-dlp download operation in a separate thread
            info_dict = await loop.run_in_executor(
                None,
                lambda: ydl.extract_info(video_url, download=True)
            )
            file_path = ydl.prepare_filename(info_dict)  # Create file name from info_dict
            print(f"Video downloaded successfully: {file_path}")
        return file_path
    except yt_dlp.utils.DownloadError as e:
        print(f"Download error: {e}")
    except ConnectionResetError as e:
        print(f"Connection was reset: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print("after download")


async def fetch_videos(user_url: str, username: str, playlist_limit: int = None) -> list:
    """Fetch video information from a user URL with an optional playlist limit."""
    if not ('@' in user_url or '/user/' in user_url):
        raise ValueError("The provided URL does not appear to be a valid TikTok user profile URL")

    ydl_opts = YT_DLP_DEFAULT_OPTS.copy()
    if playlist_limit:
        ydl_opts['playlistend'] = playlist_limit

    videos_info = []
    try:
        # Run the extraction in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(user_url, download=False)
        )
        if 'entries' in info:
            videos_info = [
                {
                    'link': entry.get('url', ''),
                    'video_id': entry.get('id', ''),
                    'tiktok_user': username,
                }
                for entry in info['entries'] if entry
            ]
    except Exception as e:
        print(f"Error extracting videos for user '{username}': {str(e)}")

    return videos_info


async def create_csv(videos: list, filename: str = "tiktok_videos.csv") -> str:
    """Create a CSV file from the list of videos."""
    os.makedirs("output", exist_ok=True)
    file_path = os.path.join("output", filename)
    headers = ["video_id", "link", "tiktok_user"]

    async with aiofiles.open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        content = [','.join(headers)] + [
            ','.join([
                str(video.get('video_id', '')),
                str(video.get('link', '')),
                str(video.get('tiktok_user', ''))
            ])
            for video in videos
        ]
        await csvfile.write('\n'.join(content))
    return file_path


async def process_users(fetch_users_func, playlist_limit=None, csv_filename="tiktok_videos.csv"):
    """Process users to fetch videos and save them into a CSV file."""
    users = fetch_users_func()
    videos = []

    for user in users:
        user_videos = await fetch_videos(user["link"], user["tiktok_user"], playlist_limit)
        print(f"Successfully crawled user: {user['tiktok_user']}")
        videos.extend(user_videos)

    csv_path = await create_csv(videos, filename=csv_filename)
    print(f"CSV created at: {csv_path}")


# Example specific methods to process users
async def process():
    await process_users(get_user_not_fetch, csv_filename="all_tiktok_videos.csv")


async def process_10():
    await process_users(get_user_fetched, playlist_limit=10, csv_filename="10_tiktok_videos.csv")

# asyncio.run(process())
# asyncio.run(process_10())
# asyncio.run(get_all_user_videos_async("https://www.tiktok.com/@tamquandeoo23", "tamquandeoo23"))
