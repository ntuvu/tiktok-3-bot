import asyncio
import os

import psutil


async def monitor_memory(interval=1):
    """
    Async function to monitor and print memory usage of the current process.
    :param interval: Time (in seconds) between memory usage checks.
    """
    process = psutil.Process(os.getpid())  # Get the current process ID
    print(f"Monitoring memory usage of process PID: {process.pid}")
    print("Press Ctrl+C to stop monitoring.\n")
    try:
        while True:
            mem_info = process.memory_info()  # Get memory information
            ram_usage_mb = mem_info.rss / 1024 / 1024  # Convert to MB
            print(f"RAM Usage: {ram_usage_mb:.2f} MB")
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        print("Memory monitoring task has been stopped.")


def start_memory_monitor(interval=1):
    """
    Starts the memory monitor task as an asyncio task.
    This allows it to integrate with asyncio properly.
    :param interval: Time (in seconds) between memory usage checks.
    """
    asyncio.create_task(monitor_memory(interval))
