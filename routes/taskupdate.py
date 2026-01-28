from fastapi import APIRouter, Depends
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from db import task_collection
from auth_dependency import get_current_user
from utils.scheduler import scheduler, schedule_task_reminder

task_update_router = APIRouter()

class TaskStatusUpdate(BaseModel):
    status: str

@task_update_router.patch("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str,
    status_update: TaskStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    task = task_collection.find_one(
        {"_id": ObjectId(task_id), "owner_id": current_user["_id"]}
    )
    if not task:
        return {"message": "Task not found"}

    new_status = status_update.status.lower()
    if new_status not in ["pending", "completed"]:
        return {"message": "Invalid status. Only 'pending' or 'completed' allowed."}

    task_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
    )

    try:
        scheduler.remove_job(str(task_id))
    except:
        pass

    if new_status == "pending" and task.get("reminder_time"):
        schedule_task_reminder(
            {**task, "status": new_status},
            current_user["email"],
            current_user.get("username", "User")
        )

    return {"message": f"Task marked as {new_status}"}
