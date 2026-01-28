from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from db import user_collection
from utils.otp_handler import generate_and_send_otp
from utils.email_utils import send_email

email_router = APIRouter()

@email_router.post("/verify-email")
async def verify_email_otp(user_id: str, otp: str):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("is_verified", False):
        return {"message": "Email already verified."}
    if user.get("email_otp") != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.utcnow() > user.get("otp_expiry"):
        raise HTTPException(status_code=400, detail="OTP expired")
    user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_verified": True}, "$unset": {"email_otp": "", "otp_expiry": ""}}
    )
    subject = "Welcome to TodoPlatform!"
    template_path = "utils/templates/welcome_message.html.j2"
    context = {"username": user["username"]}
    send_email(to_email=user["email"], subject=subject, template_path=template_path, context=context)
    return {"message": "Email verified successfully!"}

@email_router.post("/resend-email")
async def resend_verification_email(user_id: str):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("is_verified", False):
        return {"message": "Email already verified."}
    
    email = user["email"]
    username = user["username"]
    generate_and_send_otp(email, str(user["_id"]), username)
    return {"message": "Verification email resent successfully!"}
