import asyncio
from functools import wraps

from app.db_services import add_chat_id_and_user_id, get_current_tele_user_info


def auth_check(handler):
    @wraps(handler)
    async def wrapper(message, *args, **kwargs):
        chat_id = message.chat.id
        user_id = message.from_user.id
        print(f"Chat ID: {chat_id}, User ID: {user_id}")

        # add chat_id and user_id if new user
        asyncio.create_task(add_chat_id_and_user_id(chat_id, user_id))

        return await handler(message, *args, **kwargs)

    return wrapper


def roles_check(handler):
    @wraps(handler)
    async def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        user = await get_current_tele_user_info(user_id)
        role = user[0]["roles"]
        print(f"User: {user[0]["roles"]}")

        if role != "KING":
            return await message.reply("You don't have access to this command.")

        return await handler(message, *args, **kwargs)

    return wrapper
