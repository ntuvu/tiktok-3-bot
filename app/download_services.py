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

        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),  # Template for output file names
        'merge_output_format': 'mp4',  # Ensure the final merged file is MP4
    }


async def get_video_async(video_url: str) -> str:
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # Ensure download_dir exists
    ydl_opts = get_yt_dlp_options()

    # Add memory optimization options
    ydl_opts['quiet'] = True
    ydl_opts['no_warnings'] = True
    ydl_opts['progress_hooks'] = []  # Remove progress hooks to reduce overhead

    loop = asyncio.get_event_loop()

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get minimal info first
            info_dict = await loop.run_in_executor(
                None,
                lambda: ydl.extract_info(video_url, download=False)
            )

            # Check file size before downloading (optional size limit)
            if info_dict.get('filesize') and info_dict.get('filesize') > 50 * 1024 * 1024:  # 50MB
                print(f"Skipping large file: {info_dict.get('filesize') / 1024 / 1024:.2f}MB")
                return ""

            # Download with optimized options
            info_dict = await loop.run_in_executor(
                None,
                lambda: ydl.extract_info(video_url, download=True)
            )
            file_path = ydl.prepare_filename(info_dict)
            print(f"Video downloaded successfully: {file_path}")
            return file_path
    except Exception as e:
        print(f"Download error: {e}")
        return ""


async def fetch_videos(user_url: str, username: str, playlist_limit: int = None):
    """Fetch video information from a user URL with an optional playlist limit."""
    if not ('@' in user_url or '/user/' in user_url):
        raise ValueError("The provided URL does not appear to be a valid TikTok user profile URL")

    ydl_opts = YT_DLP_DEFAULT_OPTS.copy()
    if playlist_limit:
        ydl_opts['playlistend'] = playlist_limit

    # Add these options to reduce memory usage
    ydl_opts['quiet'] = True
    ydl_opts['extract_flat'] = True  # Don't extract full info
    ydl_opts['skip_download'] = True

    try:
        # Run the extraction in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(user_url, download=False)
        )

        videos_info = []
        if 'entries' in info:
            # Process entries one by one instead of creating a large list comprehension
            for entry in info['entries']:
                if entry:
                    videos_info.append({
                        'link': entry.get('url', ''),
                        'video_id': entry.get('id', ''),
                        'tiktok_user': username,
                    })

                    # Process in batches to avoid memory buildup
                    if len(videos_info) >= 100:
                        # Return this batch and process it before continuing
                        yield videos_info
                        videos_info = []

            # Return any remaining videos
            if videos_info:
                yield videos_info
    except Exception as e:
        print(f"Error extracting videos for user '{username}': {str(e)}")
        yield []


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


async def process_users(users, playlist_limit=None, csv_filename="tiktok_videos.csv"):
    """Process users to fetch videos and save them into a CSV file."""
    all_videos = []
    for user in users:
        # Collect videos from the async generator
        user_videos = []
        async for batch in fetch_videos(user["link"], user["tiktok_user"], playlist_limit):
            user_videos.extend(batch)

        print(f"Successfully crawled user: {user['tiktok_user']} - found {len(user_videos)} videos")
        all_videos.extend(user_videos)

    csv_path = await create_csv(all_videos, filename=csv_filename)
    print(f"CSV created at: {csv_path}")


# Example specific methods to process users
async def process():
    users = await get_user_not_fetch()
    await process_users(users, csv_filename="all_tiktok_videos.csv")


async def process_10():
    await process_users(await get_user_fetched(), playlist_limit=10, csv_filename="10_tiktok_videos.csv")

# asyncio.run(process())
# asyncio.run(process_10())
# asyncio.run(get_all_user_videos_async("https://www.tiktok.com/@tamquandeoo23", "tamquandeoo23"))
