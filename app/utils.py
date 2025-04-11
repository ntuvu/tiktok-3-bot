def extract_tiktok_username(url: str) -> str | None:
    # Split the URL by '/' and look for the part starting with '@'
    parts = url.split('/')
    for part in parts:
        if part.startswith('@'):
            # Return the username without the '@' symbol
            return part[1:]
    return None


def extract_link_from_caption(caption: str) -> str | None:
    # Check if 'link:' exists in the caption
    if 'link:' in caption:
        # Split by 'link:' and take the part after it
        link_part = caption.split('link:')[1]

        # If there are more fields separated by commas, take only the link part
        if ',' in link_part:
            link = link_part.split(',')[0].strip()
        else:
            link = link_part.strip()

        return link
    return None