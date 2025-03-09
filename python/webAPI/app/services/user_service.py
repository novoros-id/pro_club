from fastapi import HTTPException, status
from app.services.file_service import create_folder_structure

from app.models import UserBase

class UserService:

    def __init__(self):
        self.users_db = self.get_users_db()
 
    # Функия имитирующая БД
    # todo: переделать
    def get_users_db(self) -> dict:
        users = [
            UserBase(id="dakinfiev", username="dakinfiev"),
            UserBase(id="Jon", username="Jon"),
        ]
        return users

    def get_user_by_id(self, user_name: str) -> UserBase:
        # todo Сделать файл мэпинг ID и имен пользователей.
        # Если id найден, то возвращать класс
        return next((user for user in self.users_db if user.username == user_name), None)

    def get_user(self, user_id: str) -> UserBase:

        user = self.get_user_by_id(user_id)
        if user == None:
            user = self.create_user(user_id)
            create_folder_structure(user_id)
        return user
    
    def create_user(self, user_id: str) -> UserBase:
        user = UserBase(id=user_id, username=user_id)
        self.users_db.append(user)
        return user
        