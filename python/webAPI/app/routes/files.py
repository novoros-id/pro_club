from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from app.services.file_service import FileService
from app.services.user_service import UserService
from app.models import UserBase

file_service = FileService()
user_service = UserService(file_service)

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/")
async def read_root():
    return {"message": "root files"} 

""" @router.post("/get_files/{user_id}")
async def get_files(user_id: str):
    return await file_service.get_files_from_user(user_id) """

@router.get("/get_list_files/{user_id}")
async def get_list_files(user_id: str):
    user = user_service.get_user_by_id(user_id)
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    else:
        return file_service.get_list_files(user)