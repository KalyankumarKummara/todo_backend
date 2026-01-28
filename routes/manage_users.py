from fastapi import APIRouter, Depends, HTTPException, status
from db import user_collection, task_collection
from bson import ObjectId
from auth_dependency import admin_required

admin_router = APIRouter()

@admin_router.get("/users")
def list_users(current_admin: dict = Depends(admin_required)):
    users = list(user_collection.find({}, {"password": 0}))
    for user in users:
        user["_id"] = str(user["_id"])
    return {"total": len(users), "users": users}

@admin_router.delete("/users/{user_id}")
def delete_user(user_id: str, current_admin: dict = Depends(admin_required)):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["email"] == current_admin["email"]:
        raise HTTPException(status_code=400, detail="Admin account cannot be deleted")
    
    user_collection.delete_one({"_id": ObjectId(user_id)})
    task_collection.delete_many({"owner_id": str(user_id)})
    
    return {
        "message": f"User {user['username']} and their associated tasks deleted successfully"
    }
