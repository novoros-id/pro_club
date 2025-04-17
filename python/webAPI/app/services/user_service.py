import app.utils.io_file_operation as io_file_operation
from app.config import settings
import os
from fastapi import Depends
import app.utils.response as response_utils
from app.core.provider_db import Provider

from app.models import UserBase, CreateUser, SimpleRequest
from app.db_models import User

class UserService:

    def __init__(self):
       pass
          
    # Получение пользователя. 
    # Параметр is_create_user - означает, что функция вызывается из метода создания пользователя
    def get_user(self, 
                 user_id: str, 
                 db_provider: Provider, 
                 is_create_user: bool = False) -> UserBase:

        user = db_provider.get_user_id(user_id)
     
        if user == None and is_create_user == False:
                # Todo передаавать имя, идентифкатор и почту. Пока парается только ИД это и есть имя
                user = db_provider.create_user(user_id, user_id, "")
                io_file_operation.create_folder_structure(user)
        return user
    
    async def create_user(self, 
                    create_user: CreateUser, 
                    db_provider: Provider) -> User:
        user = self.get_user(create_user.user.id, db_provider, True)
        if user == None:
            user = db_provider.create_user(create_user.user.id, create_user.user.name, create_user.user.email)
            response_text = f'Пользователь {create_user.user.name} успешно создан!'
        else:
            response_text = f'Пользователь {create_user.user.name} уже существует!'
        simple_response = response_utils.create_simple_response_from_request(create_user, response_text)
        response = await response_utils.send_request(simple_response, "create_user")
        return user
        