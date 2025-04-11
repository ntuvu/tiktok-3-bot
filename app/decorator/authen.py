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
        try:
            user_id = message.from_user.id
            user = await get_current_tele_user_info(user_id)

            # Check if user exists and has roles
            if not user or not isinstance(user, list) or len(user) == 0:
                return await message.reply("User not found or has no role information.")

            role = user[0].get("roles")
            print(f"User: {role}")  # Fixed string formatting

            if role != "KING":
                return await message.reply("You don't have access to this command.")

            return await handler(message, *args, **kwargs)
        except Exception as e:
            print(f"Error checking roles: {e}")
            return await message.reply("An error occurred while checking permissions.")

    return wrapper  # Added missing return statement
