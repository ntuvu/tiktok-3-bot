import secrets
import string


def generate_download_string(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits
    random_str = ''.join(secrets.choice(characters) for _ in range(length))
    return f'download_{random_str}'


def extract_tiktok_video_id(url: str) -> str | None:
    """
    Extract the video ID from a TikTok URL.

    Args:
        url (str): The TikTok video URL

    Returns:
        str: The extracted video ID
    """
    # Split the URL by '/'
    parts = url.split('/')

    # Find the part that contains the video ID
    for part in parts:
        # The video part typically contains 'video' followed by the ID
        if 'video' in part:
            # Get the ID which follows 'video/'
            video_id = parts[parts.index(part) + 1]
            return video_id

    # If URL format is different and has query parameters
    if '?' in url:
        base_url = url.split('?')[0]
        parts = base_url.split('/')
        # The last non-empty part should be the video ID
        for part in reversed(parts):
            if part:
                return part

    return None
