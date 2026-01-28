from pydantic import BaseModel, EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyResetOTPRequest(BaseModel):
    user_id: str
    otp: str

class ResetPasswordRequest(BaseModel):
    user_id: str
    otp: str
    new_password: str
