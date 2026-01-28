from fastapi import APIRouter, Depends
from models.login import Login
from db  import user_collection
from passlib.context import CryptContext
from auth import create_access_token
login_router = APIRouter()

@login_router.post("/login")
async def login(user : Login):
    existing_user = user_collection.find_one({"email" : user.email})
    if not existing_user:
        return{"error": "Email not exists"}
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
    if not pwd_context.verify(user.password, existing_user["password"]):
        return {"error" : "Invalid password"}
    access_token = create_access_token({
        "sub": str(existing_user["_id"]),
        "username": existing_user.get("username", ""),
        "email": existing_user.get("email", "")

         })
    return {
        "message" : "Login successful",
        "access_token" : access_token,
        "token_type" : "bearer"
        }