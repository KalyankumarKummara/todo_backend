from pydantic import BaseModel, EmailStr
class GetUser(BaseModel):
    _id : str
    username: str
    email: EmailStr