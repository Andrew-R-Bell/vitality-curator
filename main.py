# main.py
import os
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

from bot import run_once

TIMEZONE = os.getenv("TIMEZONE", "Australia/Brisbane")
POST_TIME = os.getenv("POST_TIME", "09:00")  # HH:MM 24h

def schedule_job():
    tz = pytz.timezone(TIMEZONE)
    hour, minute = map(int, POST_TIME.split(":"))
    sched = BlockingScheduler(timezone=tz)
    sched.add_job(run_once, CronTrigger(hour=hour, minute=minute, timezone=tz))
    print(f"[Scheduler] Will post daily at {POST_TIME} ({TIMEZONE}).", flush=True)
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        print("[Scheduler] Stopped.")

if __name__ == "__main__":
    if os.getenv("RUN_NOW"):
        run_once()
        sys.exit(0)
    schedule_job()