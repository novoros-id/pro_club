from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from app.services.user_service import UserService
from app.services.file_service import FileService
from app.models import UserRequest

file_service = FileService()
user_service = UserService(file_service)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def read_root():
    return {"message": "root users"} 

""" @router.post("/{user_id}")
async def get_user(user_id: str):
    return await user_service.get_user_by_id(user_id) """

@router.post("/check_user")
async def check_user(user_check: UserRequest):
    return await user_service.check_user(user_check)