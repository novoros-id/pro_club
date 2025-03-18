from fastapi import Depends, FastAPI
from typing import Annotated
from app.models import UserBase, SimpleRequest
from app.services.user_service import UserService

user_service = UserService()

def get_user(request: SimpleRequest) -> UserBase:

    return user_service.get_user(request.code_uid.username)

CurrentUser = Annotated[UserBase, Depends(get_user)]