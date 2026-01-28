from fastapi import APIRouter, Depends
from auth_dependency import get_current_user
from db import task_collection
from datetime import datetime

user_stats_router = APIRouter()

@user_stats_router.get("/tasks/stats")
async def get_task_stats(current_user: dict = Depends(get_current_user)):
    user_id = current_user["_id"]

    total_tasks = task_collection.count_documents({"owner_id": user_id})
    completed_tasks = task_collection.count_documents({"owner_id": user_id, "status": "completed"})
    pending_tasks = task_collection.count_documents({"owner_id": user_id, "status": {"$ne": "completed"}})
    overdue_tasks = task_collection.count_documents({
        "owner_id": str(user_id),
        "status": {"$ne": "completed"},
        "due_date": {"$lt": datetime.utcnow()}
    })

    high_priority = task_collection.count_documents({"owner_id": user_id, "priority": "high"})
    medium_priority = task_collection.count_documents({"owner_id": user_id, "priority": "medium"})
    low_priority = task_collection.count_documents({"owner_id": user_id, "priority": "low"})

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "priority_breakdown": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        }
    }
