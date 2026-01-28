from fastapi import APIRouter, HTTPException
from bson import ObjectId
from db import user_collection
from utils.reset_password import send_reset_otp, reset_password
from datetime import datetime, timezone
from models.forgot_password import (
    ForgotPasswordRequest,
    VerifyResetOTPRequest,
    ResetPasswordRequest,
)

forgot_password_router = APIRouter()

@forgot_password_router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    user = user_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    send_reset_otp(user["email"], str(user["_id"]), user["username"])
    return {
        "success": True,
        "message": "Password reset OTP sent to your email.",
        "user_id": str(user["_id"])
    }

@forgot_password_router.post("/verify-reset-otp")
async def verify_reset_otp(request: VerifyResetOTPRequest):
    user = user_collection.find_one({"_id": ObjectId(request.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("reset_otp") != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    reset_expiry = user.get("reset_expiry")
    if not reset_expiry:
        raise HTTPException(status_code=400, detail="OTP expired")

    if isinstance(reset_expiry, (int, float)):
        reset_expiry = datetime.fromtimestamp(reset_expiry / 1000, tz=timezone.utc)
    elif isinstance(reset_expiry, datetime):
        if reset_expiry.tzinfo is None:
            reset_expiry = reset_expiry.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > reset_expiry:
        raise HTTPException(status_code=400, detail="OTP expired")

    return {"message": "OTP verified successfully"}

@forgot_password_router.post("/reset-password")
async def reset_user_password(request: ResetPasswordRequest):
    result = reset_password(request.user_id, request.otp, request.new_password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "message": "Password has been reset successfully."}


@forgot_password_router.post("/resend-reset-otp")
async def resend_reset_otp(request: ForgotPasswordRequest):
    user = user_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    send_reset_otp(user["email"], str(user["_id"]), user["username"])
    return {
        "success": True,
        "message": "Password reset OTP resent successfully.",
        "user_id": str(user["_id"])
    }
