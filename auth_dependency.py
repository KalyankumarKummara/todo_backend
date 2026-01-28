from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth import verify_access_token
from db import user_collection
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

oauth2scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2scheme)):
    payload = verify_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token",
            headers = {"WWW-Authenticate":"Bearer"}
        ) 
    user = user_collection.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")  
    if user["email"] == ADMIN_EMAIL:
        user["role"] = "admin"
    else:
        user["role"] = "user"

    user["_id"]  = str(user["_id"])   
    user.pop("password", None) 
    return user

def admin_required(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
