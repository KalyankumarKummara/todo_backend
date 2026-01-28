from fastapi import APIRouter
from models.signup import Signup
from db import user_collection
from passlib.context import CryptContext
from bson import ObjectId
from utils.otp_handler import generate_and_send_otp
signup_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
@signup_router.post("/signup")
async def Signup(user : Signup):
    if user.password != user.Confirm_password:
        return {"message" : "Passwords do not match"}
    existing_user = user_collection.find_one({"email" : user.email})
    if existing_user:
        return {"message": "User with this email already exists"}
    hashed_password = pwd_context.hash(user.password)
    user_dict = {
        "username" : user.username,
        "email" : user.email,
        "password" : hashed_password,
        "is_verified" : False 
    }
    result = user_collection.insert_one(user_dict)
    generate_and_send_otp(user.email, str(result.inserted_id), user.username)
    return {"success" : True, "message" : "User created successfully. OTP sent to email for verification ", "user_id" : str(result.inserted_id)}