from fastapi import APIRouter, Depends, Body, HTTPException, status
from auth_dependency import get_current_user
from db import user_collection, task_collection
from bson import ObjectId
from datetime import datetime
from passlib.context import CryptContext

profile_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@profile_router.get("/user/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    user = user_collection.find_one({"_id": ObjectId(current_user["_id"])})
    if not user:
        return {"error": "User not found"}
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return user

@profile_router.put("/user/profile")
async def update_profile(
    username: str = Body(None),
    password: str = Body(None),
    current_user: dict = Depends(get_current_user)
):
    user_id = ObjectId(current_user["_id"])
    updates = {}
    if username:
        updates["username"] = username
    if password:
        updates["password"] = pwd_context.hash(password)
    if not updates:
        return {"message": "No updates provided"}
    updates["updated_at"] = datetime.utcnow()
    user_collection.update_one({"_id": user_id}, {"$set": updates})
    return {"message": "Profile updated successfully"}

@profile_router.delete("/delete")
async def delete_account(current_user: dict = Depends(get_current_user)):
    user_id = ObjectId(current_user["sub"])

    deleted_user = user_collection.delete_one({"_id": user_id})
    task_collection.delete_many({"owner_id": str(user_id)})

    if deleted_user.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "Account and all tasks deleted successfully"}