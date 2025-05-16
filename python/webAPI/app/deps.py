from fastapi import Depends, FastAPI
from typing import Annotated
from collections.abc import Generator
from sqlmodel import Session
from app.models import UserBase, SimpleRequest
from app.core.provider_db import Provider, DatabaseProvider, FileProvider
from app.config import settings

def get_db_provider() -> Provider:
    if settings.USE_DB == True:
        return Provider(DatabaseProvider())
    else:
        return Provider(FileProvider(""))
    
""" def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session """

def get_user(request: SimpleRequest, db_provider: Provider = Depends(get_db_provider)) -> UserBase:

    from app.services.user_service import UserService

    user_id = request.code_uid.username
    user_service = UserService()
    return user_service.get_user(user_id, db_provider)


DB_Provider = Annotated[Provider, Depends(get_db_provider)]
CurrentUser = Annotated[UserBase, Depends(get_user)]
#CurrentSessionDB = Annotated[Session, Depends(get_db)]
