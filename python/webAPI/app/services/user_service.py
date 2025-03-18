import app.utils.io_file_operation as io_file_operation
from app.config import settings
import os

from app.models import UserBase

class UserService:

    def __init__(self):
        self.users_db = self.get_users_db()
 
    # Функия имитирующая БД
    # todo: переделать
    def get_users_db(self) -> dict:
        users = []
        main_folder_path = settings.MAIN_FOLDER_PATH

        # Получаем все папки в каталоге MAIN_FOLDER_PATH
        for folder_name in os.listdir(main_folder_path):
            folder_path = os.path.join(main_folder_path, folder_name)
            if os.path.isdir(folder_path):
                # Создаем объект UserBase для каждой папки
                user_id = folder_name #todo: пока ID пользователя этоя имя папки
                users.append(UserBase(id=user_id, username=folder_name))
        """  users = [
            UserBase(id="dakinfiev", username="dakinfiev"),
            UserBase(id="Jon", username="Jon"),
        ] """
        return users

    def get_user_by_id(self, user_name: str) -> UserBase:
        # todo Сделать файл мэпинг ID и имен пользователей.
        # Если id найден, то возвращать класс
        return next((user for user in self.users_db if user.username == user_name), None)

    def get_user(self, user_id: str) -> UserBase:

        user = self.get_user_by_id(user_id)
        if user == None:
            user = self.create_user(user_id)
            io_file_operation.create_folder_structure(user)
        return user
    
    def create_user(self, user_id: str) -> UserBase:
        user = UserBase(id=user_id, username=user_id)
        self.users_db.append(user)
        return user
        