import random
from datetime import datetime, timedelta
from bson import ObjectId
from db import user_collection
from utils.email_utils import send_email
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
RESET_EXPIRE_MINUTES = 10

def send_reset_otp(user_email: str, user_id: str, username: str):
    otp = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=RESET_EXPIRE_MINUTES)

    user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"reset_otp": otp, "reset_expiry": expiry}}
    )

    subject = "Reset Your Password - TodoPlatform"
    template_path = "utils/templates/reset_password_template.html.j2"
    context = {"otp": otp, "username": username}
    send_email(to_email=user_email, subject=subject, template_path=template_path, context=context)
    return otp

def reset_password(user_id: str, otp: str, new_password: str):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return {"error": "User not found"}

    if user.get("reset_otp") != otp:
        return {"error": "Invalid OTP"}

    if datetime.utcnow() > user.get("reset_expiry"):
        return {"error": "OTP expired"}

    hashed_password = pwd_context.hash(new_password)
    user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed_password},
        "$unset": {"reset_otp": "", "reset_expiry": ""}}
    )
    return {"message": "Password reset successful"}
