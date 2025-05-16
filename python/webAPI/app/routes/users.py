from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from app.services.user_service import UserService
from app.models import CreateUser
from app.deps import get_db_provider
from app.core.provider_db import Provider

user_service = UserService()

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def read_root():
    return {"message": "root users"} 

@router.post("/create")
async def create_user(create_user: CreateUser, db_provider: Provider = Depends(get_db_provider)):
    return await user_service.create_user(create_user, db_provider)