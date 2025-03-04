from fastapi import HTTPException, status
from app.services.file_service import FileService

from app.models import UserRequest, UserBase

class UserService:

    def __init__(self, file_service: FileService):
        self.file_service = file_service
        self.users_db = self.get_users_db()
 
    # Функия имитирующая БД
    def get_users_db(self) -> dict:
        users = [
            UserBase(username="dakinfiev"),
            UserBase(username="Jon"),
        ]
        return users

    def get_user_by_id(self, user_name: str) -> UserBase:
        # todo Сделать файл мэпинг ID и имен пользователей.
        # Если id найден, то возвращать класс
        return next((user for user in self.users_db if user.username == user_name), None)


        """ else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") """


    async def check_user(self, user_check: UserRequest) -> bool:

        user = self.get_user_by_id(user_check.username)
        if user == None:
            user = self.create_user(user_check)
            self.file_service.create_folder_structure(user.name)
        return True
    

        