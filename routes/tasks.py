from fastapi import APIRouter, Depends, Query
from auth_dependency import get_current_user
from db import task_collection
from models.tasks import Task
from datetime import datetime, timezone
from bson import ObjectId
from utils.scheduler import scheduler,schedule_task_reminder

task_router = APIRouter()

def serialize_task(task: dict):
    task["_id"] = str(task["_id"])

    if task.get("due_date"):
        task["due_date"] = task["due_date"].date().isoformat()

    if task.get("reminder_time"):
        task["reminder_time"] = (
            task["reminder_time"]
            .replace(tzinfo=timezone.utc)
            .isoformat()
        )

    return task


@task_router.post("/tasks")
async def create_task(task : Task, current_user : dict = Depends(get_current_user)):
    task_data = task.dict()
    task_data.update({
        "owner_id" : current_user["_id"],
        "owner_email" : current_user["email"],
        "created_at" : datetime.utcnow(),
        "updated_at" : datetime.utcnow()
    })
    result = task_collection.insert_one(task_data)
    task_data["_id"] = result.inserted_id
    if task.reminder_time:
        schedule_task_reminder(task_data, current_user["email"], current_user.get("username", "User"))
       
    return {"message" : "Task created successfully", "task_id" : str(result.inserted_id)}


@task_router.get("/tasks")
async def get_tasks(
    status: str = None,
    priority: str = None,
    tags: str = Query(None),
    search: str = None,
    limit : int = 10,
    skip: int = 0,
    sort_by : str = "created_at",
    order : str = "desc",
    current_user : dict = Depends(get_current_user)
):
    query = {"owner_id": current_user["_id"]}

    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    if tags:
        query["tags"] = {"$all": tags.split(",")}

    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"priority": {"$regex": search, "$options": "i"}},
            {"status": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}},
            

        ]

    sort_order = 1 if order == "asc" else -1
    allowed_sort_fields = {"created_at", "due_date", "priority"}
    sort_field = sort_by if sort_by in allowed_sort_fields else "created_at"

    tasks = (
        task_collection.find(query)
        .sort(sort_field, sort_order)
        .skip(skip)
        .limit(limit)
    )

    result = []
    for task in tasks:
       result.append(serialize_task(task))

    total_count = task_collection.count_documents(query)
    return {
    "tasks": result,
    "count": len(result),       
    "total_count": total_count   
}
    
@task_router.get("/tasks/{task_id}")
async def get_task(task_id : str, current_user : dict = Depends(get_current_user)):
    task = task_collection.find_one({"_id" : ObjectId(task_id), "owner_id" : current_user["_id"]})
    if task:
        return serialize_task(task)
    return {"message" : "Task not found"}

@task_router.put("/tasks/{task_id}")
async def update_task(task_id : str, updated_task : Task, current_user : dict = Depends(get_current_user)):
    existing_task = task_collection.find_one({"_id" : ObjectId(task_id), "owner_id" : current_user["_id"]})
    if not existing_task : 
        return {"message" : "Task not found"}
    updated_data = updated_task.dict(exclude_unset=True)
    updated_data.pop("owner_id",None)
    updated_data.pop("created_at",None)
    updated_data["updated_at"] = datetime.utcnow()

    result = task_collection.update_one({"_id" : ObjectId(task_id)}, {"$set" : updated_data})
    if result.modified_count == 0 : 
        return {"message" : "No changes made to the task"}
    if "reminder_time" in updated_data:
        try:
            scheduler.remove_job(str(task_id))
        except:
            pass
    updated_task_doc = task_collection.find_one({"_id": ObjectId(task_id)})
    if updated_task_doc and updated_task_doc.get("reminder_time"):
            schedule_task_reminder(
                updated_task_doc,
                current_user["email"],
                current_user.get("username", "User")
            )
    return {"message" : "Task updated successfully"}

@task_router.delete("/tasks/{task_id}")
async def delete_task(task_id : str, current_user : dict = Depends(get_current_user)):
    existing_task = task_collection.delete_one({"_id" : ObjectId(task_id), "owner_id" : current_user["_id"]})
    if existing_task.deleted_count == 0 : 
        return {"error" : "Task not found"}
    try:
        scheduler.remove_job(str(task_id))
    except:
        pass
    return {"message" : "Task deleted successfully"}    