from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from db import task_collection, user_collection
from utils.email_utils import send_reminder_email

cron_router = APIRouter()

@cron_router.post("/cron/send-reminders")
def send_due_reminders():
    now = datetime.now(timezone.utc)
    past_5_min = now - timedelta(minutes=5)
    next_5_min = now + timedelta(minutes=5)

    tasks = task_collection.find({
        "reminder_time": {
            "$gte": past_5_min,
            "$lte": next_5_min
        },
        "status": {"$ne": "completed"}
    })

    sent = 0

    for task in tasks:
        user = user_collection.find_one({"_id": task["owner_id"]})
        if not user:
            continue

        send_reminder_email(
            to_email=user["email"],
            username=user.get("username", "User"),
            title=task["title"],
            description=task.get("description"),
            priority=task.get("priority", "medium"),
            due_date=task.get("due_date")
        )

        sent += 1

    return {"status": "ok", "sent": sent}
