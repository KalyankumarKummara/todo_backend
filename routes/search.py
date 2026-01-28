from fastapi import APIRouter, Depends
from auth_dependency import get_current_user
from db import task_collection

search_router = APIRouter(prefix="/search", tags=["Search"])

@search_router.get("")
def global_search(q: str, current_user=Depends(get_current_user)):
    query = q.strip()
    owner_id = current_user["_id"]
    keywords = [word for word in query.split(" ") if word]
    or_conditions = []
    for word in keywords:
        regex = {"$regex": word, "$options": "i"}
        or_conditions.extend([
            {"title": regex},
            {"description": regex},
            {"status": regex},
            {"priority": regex},
            {"tags": regex} 
        ])

    results = task_collection.find(
        {
            "owner_id": owner_id,
            "$or": or_conditions if or_conditions else []
        }
    )

    return [
        {
            "_id": str(task["_id"]),
            "title": task.get("title"),
            "description": task.get("description"),
            "status": task.get("status"),
            "priority": task.get("priority"),
            "tags": task.get("tags", [])
        }
        for task in results
    ]
