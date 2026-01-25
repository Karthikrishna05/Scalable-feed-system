from celery import shared_task
import time
@shared_task
def debug_task(duration):
    print(f"debug_task: Starting work for {duration} seconds...")
    time.sleep(duration)
    print("debug_task: Work finished!")
    return "Done"