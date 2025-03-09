from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from app.services.user_service import UserService
from app.models import SimpleRequest
from app.deps import CurrentUser

user_service = UserService()

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def read_root():
    return {"message": "root users"} 

@router.post("/check_user")
async def check_user(request: SimpleRequest, user: CurrentUser):
    return await user_service.get_user_by_id(user)