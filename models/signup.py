from pydantic import BaseModel, EmailStr
class Signup(BaseModel):
    username: str
    email: EmailStr
    password : str
    Confirm_password : str