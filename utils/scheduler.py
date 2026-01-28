from datetime import datetime, timezone
import os
from bson import ObjectId

from db import task_collection, user_collection
from utils.email_utils import send_reminder_email

# =====================================================
# Environment flag
# =====================================================
ENV = os.getenv("ENV", "production")

# =====================================================
# SAFE DEFAULTS (PRODUCTION)
# These prevent crashes when APScheduler is disabled
# =====================================================
scheduler = None

def schedule_task_reminder(*args, **kwargs):
    # Scheduler disabled in production
    return

def start_scheduler():
    # Scheduler disabled in production
    return


# =====================================================
# LOCAL ENVIRONMENT ONLY (APScheduler ENABLED)
# =====================================================
if ENV == "local":
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.triggers.cron import CronTrigger
    from jinja2 import Environment, FileSystemLoader

    scheduler = AsyncIOScheduler()

    template_path = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_path))

    def schedule_task_reminder(task, user_email, username):
        if not task.get("reminder_time"):
            return

        reminder_time = task["reminder_time"]

        if isinstance(reminder_time, datetime) and reminder_time.tzinfo is None:
            reminder_time = reminder_time.replace(tzinfo=timezone.utc)

        reminder_type = task.get("reminder_type", "once")

        if reminder_type == "once" and reminder_time < datetime.now(timezone.utc):
            return

        def send_reminder():
            print(f"[SCHEDULER] Reminder triggered for task {task['_id']} → {user_email}")

            send_reminder_email(
                to_email=user_email,
                username=username,
                title=task["title"],
                description=task.get("description", "No description"),
                priority=task.get("priority", "medium"),
                due_date=task.get("due_date")
            )

        if reminder_type == "once":
            trigger = DateTrigger(run_date=reminder_time)

        elif reminder_type == "daily":
            trigger = CronTrigger(
                hour=reminder_time.hour,
                minute=reminder_time.minute,
                timezone=timezone.utc
            )

        elif reminder_type == "weekly":
            trigger = CronTrigger(
                day_of_week=reminder_time.weekday(),
                hour=reminder_time.hour,
                minute=reminder_time.minute,
                timezone=timezone.utc
            )

        elif reminder_type == "monthly":
            trigger = CronTrigger(
                day=reminder_time.day,
                hour=reminder_time.hour,
                minute=reminder_time.minute,
                timezone=timezone.utc
            )

        else:
            print(f"[SCHEDULER] Unknown reminder type: {reminder_type}")
            return

        scheduler.add_job(
            send_reminder,
            trigger,
            id=str(task["_id"]),
            replace_existing=True
        )

    def load_existing_reminders():
        tasks = task_collection.find({
            "reminder_time": {"$ne": None},
            "status": {"$ne": "completed"}
        })

        for task in tasks:
            try:
                owner_id = ObjectId(task["owner_id"])
            except Exception:
                owner_id = task["owner_id"]

            user = user_collection.find_one({"_id": owner_id})
            if not user:
                continue

            schedule_task_reminder(
                task,
                user["email"],
                user.get("username", "User")
            )

    def start_scheduler():
        scheduler.start()
        load_existing_reminders()
        print("[SCHEDULER] Active jobs:", scheduler.get_jobs())
