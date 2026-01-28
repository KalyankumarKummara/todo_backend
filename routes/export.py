from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from auth_dependency import get_current_user
from db import task_collection
from io import StringIO
import csv

export_router = APIRouter()

@export_router.get("/tasks/export/csv")
async def export_tasks_csv(current_user: dict = Depends(get_current_user)):
    user_id = current_user["_id"]

    tasks = list(task_collection.find({"owner_id": user_id}))

    if not tasks:
        return {"message": "No tasks found to export"}

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["title", "description", "status", "priority", "due_date"])

    for task in tasks:
        writer.writerow([
            task.get("title", ""),
            task.get("description", ""),
            task.get("status", ""),
            task.get("priority", ""),
            task.get("due_date").strftime("%Y-%m-%d %H:%M") if task.get("due_date") else ""
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks.csv"}
    )
