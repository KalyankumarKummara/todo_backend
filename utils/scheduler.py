from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader
from main import ENV
from utils.email_utils import send_reminder_email
from db import task_collection, user_collection
import os
from bson import ObjectId
if ENV == "local":
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()
template_path = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(template_path))

def schedule_task_reminder(task, user_email, username):
    if not task.get("reminder_time"):
        return

    reminder_time = task["reminder_time"]
    if isinstance(reminder_time, datetime) and reminder_time.tzinfo is None:
        reminder_time = reminder_time.replace(tzinfo=timezone.utc)
    reminder_type = task.get("reminder_type","once")

    if reminder_type == "once" and reminder_time < datetime.now(timezone.utc):
        return
    
    def send_reminder():
        print(f"Reminder triggered for task {task['_id']} to {user_email}")
        template = env.get_template("reminder_template.html.j2")
        priority_colors = {
            "high": "#e53935",
            "medium": "#ff9800",
            "low": "#43a047"
        }
        html_content = template.render(
            username=username,
            title=task["title"],
            description=task.get("description", "No description"),
            priority=task.get("priority", "medium"),
            priority_color=priority_colors.get(task.get("priority", "medium"), "#333"),
            due_date=task.get("due_date", "No due date")
        )
        send_reminder_email(user_email,
    username,
    task["title"],
    task.get("description", "No description"),
    task.get("priority", "medium"),
    task.get("due_date", None))
        
    if reminder_type == "once":
        print(f"[SCHEDULER] Using DateTrigger for task {task['_id']}")
        trigger = DateTrigger(run_date=reminder_time)
    elif reminder_type == "daily":
        print(f"[SCHEDULER] Using Daily CronTrigger for task {task['_id']}")
        trigger = CronTrigger(hour = reminder_time.hour, minute = reminder_time.minute, timezone = timezone.utc)
    elif reminder_type == "weekly":
        print(f"[SCHEDULER] Using Weekly CronTrigger for task {task['_id']} on weekday {reminder_time.weekday()}")
        trigger = CronTrigger(day_of_week = reminder_time.weekday(),hour = reminder_time.hour, minute = reminder_time.minute, timezone = timezone.utc)
    elif reminder_type == "monthly":
        print(f"[SCHEDULER] Using Monthly CronTrigger for task {task['_id']} on day {reminder_time.day}")
        trigger = CronTrigger(day = reminder_time.day, hour = reminder_time.hour , minute = reminder_time.minute, timezone = timezone.utc)
    else:
        print(f"[SCHEDULER] unknown reminder type: {reminder_type}")

    scheduler.add_job(send_reminder, trigger, id=str(task["_id"]), replace_existing=True)

from bson import ObjectId

def load_existing_reminders():
    tasks = task_collection.find({"reminder_time": {"$ne": None}, "status" : {"$ne" : "completed"}})
    for task in tasks:
        try:
            owner_id = ObjectId(task["owner_id"])
        except Exception:
            owner_id = task["owner_id"]  
        
        user = user_collection.find_one({"_id": owner_id})
        if not user:
            continue

        schedule_task_reminder(task, user["email"], user.get("username", "User"))


def start_scheduler():
    scheduler.start()
    load_existing_reminders()
    print("Current scheduled jobs:", scheduler.get_jobs())

