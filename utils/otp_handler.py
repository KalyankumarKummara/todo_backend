import random
from datetime import datetime, timedelta
from bson import ObjectId
from db import user_collection
from utils.email_utils import send_email

OTP_EXPIRE_MINUTES = 10

def generate_and_send_otp(user_email: str, user_id: str, username: str):
    otp = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)

    user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"email_otp": otp, "otp_expiry": expiry}}
    )

    subject = "Welcome to TodoPlatform! Verify Your Email"
    template_path = "utils/templates/email_verification_template.html.j2"
    context = {"otp": otp, "username": username}
    send_email(to_email=user_email, subject=subject, template_path=template_path, context=context)

    return otp
