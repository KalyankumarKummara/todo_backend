from fastapi import APIRouter, Depends, status, HTTPException
from bson import ObjectId
from auth_dependency import get_current_user
from models.get_user import GetUser
from auth_dependency import get_current_user
from db import user_collection
from passlib.context import CryptContext
users_router = APIRouter(prefix="/users", tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@users_router.get("/me", response_model=GetUser)
def get_current_user_details(current_user: dict = Depends(get_current_user)):
    """
    Return currently logged-in user's username and email.
    """
    return {
        "_id" : str(current_user["_id"]),
        "username": current_user.get("username"),
        "email": current_user.get("email")
        
    }
@users_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(current_user=Depends(get_current_user)):
    db_user = user_collection.find_one(
        {"email": current_user["email"]}
    )

    if not db_user:
        return

    user_collection.delete_one({"_id": db_user["_id"]})

    return

@users_router.post("/verify-password")
def verify_password(
    payload: dict,
    current_user=Depends(get_current_user)
):
    password = payload.get("password")

    if not password:
        raise HTTPException(status_code=400, detail="Password required")

    db_user = user_collection.find_one(
        {"email": current_user["email"]}
    )

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    return {"verified": True}
    
