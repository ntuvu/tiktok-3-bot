# app/rate_limiter.py
import time
from collections import defaultdict
from functools import wraps
from typing import Dict, Callable, Any, TypeVar, Optional

T = TypeVar('T', bound=Callable[..., Any])


class RateLimiter:
    """Class to handle rate limiting for bot commands."""

    def __init__(self):
        # Store for rate limiting data: {user_id: {command_name: last_used_timestamp}}
        self.store: Dict[int, Dict[str, float]] = defaultdict(
            lambda: defaultdict(lambda: 0)
        )

    def check_cooldown(self, user_id: int, command_name: str, cooldown_period: int) -> Optional[int]:
        """
        Check if a user needs to wait before executing another command.

        Args:
            user_id: The user's ID
            command_name: The name of the command being executed
            cooldown_period: Time in seconds that must pass between command executions

        Returns:
            None if user can execute command, otherwise seconds remaining until allowed
        """
        current_time = time.time()
        last_time = self.store[user_id][command_name]

        # Check if cooldown period has passed
        time_since_last_call = current_time - last_time
        if last_time == 0 or time_since_last_call >= cooldown_period:
            # Update last execution time
            self.store[user_id][command_name] = current_time
            return None

        # User needs to wait
        time_remaining = int(cooldown_period - time_since_last_call) + 1  # +1 to round up
        return time_remaining

    def limit(self, cooldown: int = 5,
              error_message: str = "Command cooldown active.") -> Callable[[T], T]:
        """
        Rate limiter decorator that enforces a cooldown between command executions.

        Args:
            cooldown: Time in seconds that must pass between command executions
            error_message: Message to send when cooldown is active

        Example usage:
            @rate_limiter.limit(cooldown=5, error_message="Please wait before using this command again.")
            async def handle_command(message: types.Message):
                # Command handler code
        """

        def decorator(func: T) -> T:
            @wraps(func)
            async def wrapper(message, *args, **kwargs):
                user_id = message.from_user.id
                command_name = func.__name__

                time_remaining = self.check_cooldown(user_id, command_name, cooldown)
                if time_remaining is not None:
                    user_message = f"{error_message}"
                    return await message.answer(user_message)

                return await func(message, *args, **kwargs)

            return wrapper

        return decorator


# Create singleton instance
rate_limiter = RateLimiter()


# Maintain backwards compatibility
def rate_limit(cooldown: int, message: str = "Rate limit exceeded. Please try again later."):
    return rate_limiter.limit(cooldown=cooldown, error_message=message)
