from fastapi import HTTPException, status
from app.services.file_service import FileService

from app.models import UserBase, UserCheck

class UserService:

    def __init__(self, file_service: FileService):
        self.file_service = file_service
        self.users_db = self.get_users_db()
 
    def get_users_db(self) -> dict:
        users = [
            UserBase(id="1", name="dakinfiev", email=""),
            UserBase(id="2", name="Jon", email=""),
        ]
        return users

    def get_user_by_id(self, user_id: str) -> UserBase:
        # todo Сделать файл мэпинг ID и имен пользователей.
        # Если id найден, то возвращать класс
        return next((user for user in self.users_db if user.id == user_id), None)


        """ else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") """


    async def check_user(self, user_check: UserCheck) -> bool:

        user = self.get_user_by_id(user_check.id)
        if user == None:
            user = self.create_user(user_check)
            self.file_service.create_folder_structure(user.name)
        return True
    
    def create_user(self, user_check: UserCheck) -> UserBase:
        return UserBase(id = user_check.id, name=user_check.name, email="")
        