import asyncio
import os

import psutil


async def monitor_memory(interval, alert_threshold_mb=700):
    """
    Async function to monitor memory usage of the current process.
    :param interval: Time (in seconds) between memory usage checks.
    :param alert_threshold_mb: Alert if memory usage exceeds this threshold (in MB).
    """
    process = psutil.Process(os.getpid())
    print(f"Monitoring memory usage of process PID: {process.pid}")

    peak_usage = 0

    try:
        while True:
            mem_info = process.memory_info()
            ram_usage_mb = mem_info.rss / 1024 / 1024

            if ram_usage_mb > peak_usage:
                peak_usage = ram_usage_mb

            if ram_usage_mb > alert_threshold_mb:
                print(f"⚠️ HIGH MEMORY ALERT: {ram_usage_mb:.2f} MB (threshold: {alert_threshold_mb} MB)")

            # Print memory usage every interval (5 seconds)
            print(f"RAM Usage: {ram_usage_mb:.2f} MB (Peak: {peak_usage:.2f} MB)")

            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        print("Memory monitoring task has been stopped.")


def start_memory_monitor(interval):
    """
    Starts the memory monitor task as an asyncio task.
    This allows it to integrate with asyncio properly.
    :param interval: Time (in seconds) between memory usage checks.
    """
    asyncio.create_task(monitor_memory(interval))
