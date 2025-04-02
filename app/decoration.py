from functools import wraps


def log_chat_id(handler):
    """
    Decorator to print chat_id for every bot command.
    """

    @wraps(handler)
    async def wrapper(message, *args, **kwargs):
        chat_id = message.chat.id
        user_id = message.from_user.id
        print(f"Chat ID: {chat_id}, User ID: {user_id}")

        return await handler(message, *args, **kwargs)

    return wrapper
