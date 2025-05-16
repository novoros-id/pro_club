from abc import ABC, abstractmethod
from typing import Any, List
import os
from sqlalchemy.orm import Session
from app.db_models import User, Program, ConnectionSetting
from app.models import UserBase, ProgramConnectionBase
from app.config import settings
from app.core.db import engine

from app.utils.io_file_operation import get_database_config

# Абстрактный класс (интерфейс)
class DataProvider(ABC):

    @abstractmethod
    def get_user_id(self, user_id: str) -> UserBase:
        pass
    
    @abstractmethod
    def create_user(self, user_id: str, user_name: str, email:str) -> UserBase:
        pass
    
    @abstractmethod
    def get_connection_settings(self, program_uid: str) -> Any:
        pass

    @abstractmethod
    def upsert_connection_settings(self, program_connection: ProgramConnectionBase) -> Any:
        pass

# Реализация для базы данных
class DatabaseProvider(DataProvider):
    def __init__(self):
        self.session = Session(engine)

    def get_user_id(self, user_id: str) -> UserBase:
        user = self.session.query(User).filter_by(id=user_id).first()
        if user == None:
            return user
        return UserBase.model_validate(user)
    
    def create_user(self, user_id: str, user_name: str, email:str) -> User:
        user_db = User(
            id=user_id,
            name=user_name,
            email=email
        )   

        self.session.add(user_db)
        self.session.commit()
        self.session.refresh(user_db)  # Обновление объекта из базы данных
        return user_db
        
    def get_connection_settings(self, program_uid: str) -> Any:
        client_data = self.session.query(Program).filter_by(program_uid=program_uid).first()
        program_connection = ProgramConnectionBase(
            program_uid=client_data.program_uid,
            name=client_data.name,
            clienttype=client_data.clienttype,
            description=client_data.description,
            url=client_data.connection_settings.url,
            client_login=client_data.connection_settings.client_login,
            сlient_pass=client_data.connection_settings.client_pass,
            endpoint=client_data.connection_settings.endpoint
        )
        return program_connection
    
    def upsert_connection_settings(self, program_connection: ProgramConnectionBase) -> Any:
        client_data = self.session.query(Program).filter_by(program_uid=program_connection.program_uid).first()
        if client_data == None:
            client_data = Program(
                program_uid=program_connection.program_uid,
                name=program_connection.name,
                clienttype=program_connection.clienttype,
                description=program_connection.description
            )
            self.session.add(client_data)
            self.session.commit()
            self.session.refresh(client_data)

            connection_settings = ConnectionSetting(
                program_uid = program_connection.program_uid,
                url = program_connection.url,
                client_login = program_connection.client_login,  
                client_pass = program_connection.client_pass,
                endpoint = program_connection.endpoint
            )
            client_data.connection_settings = connection_settings
            self.session.add()
        else:
            client_data.name = program_connection.name
            client_data.clienttype = program_connection.clienttype
            client_data.description = program_connection.description
            client_data.connection_settings.url = program_connection.url
            client_data.connection_settings.client_login = program_connection.client_login
            client_data.connection_settings.client_pass = program_connection.client_pass
            client_data.connection_settings.endpoint = program_connection.endpoint
            self.session.commit()
        return client_data
    

# Реализация для файла
class FileProvider(DataProvider):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_user_id(self, user_id: str) -> UserBase:

        users = []
        main_folder_path = settings.MAIN_FOLDER_PATH

        # Получаем все папки в каталоге MAIN_FOLDER_PATH
        for folder_name in os.listdir(main_folder_path):
            folder_path = os.path.join(main_folder_path, folder_name)
            if os.path.isdir(folder_path):
                # Создаем объект UserBase для каждой папки
                user_id = folder_name #todo: пока ID пользователя этоя имя папки
                users.append(UserBase(id=user_id, name=folder_name, email=""))

        return next((user for user in users if user.id == user_id), None)

    def create_user(self, user_id: str, user_name: str, email:str) -> User:
        user = UserBase(id=user_id, name=user_name, email=email)
        return user
    
    def get_connection_settings(self, program_uid: str) -> Any:
        client_data = get_database_config(program_uid)
        program_connection = ProgramConnectionBase(
            program_uid=client_data['program_uid'],
            name='',
            clienttype=client_data['clienttype'],
            description='',
            url=client_data['url'],
            client_login=client_data['client_login'],
            сlient_pass=client_data['client_pass'],
            endpoint=client_data['endpoint']
        )
        return program_connection
    
    def upsert_connection_settings(self, program_connection: ProgramConnectionBase) -> Any:
        pass
   

# Класс-провайдер
class Provider:
    def __init__(self, strategy: DataProvider):
        self.strategy = strategy

    def get_user_id(self, user_id: str) -> UserBase:
        return self.strategy.get_user_id(user_id)

    def create_user(self, user_id: str, user_name: str, email:str) -> User:
        return self.strategy.create_user(user_id, user_name, email)
    
    def get_connection_settings(self, program_uid: str) -> Any:
        return self.strategy.get_connection_settings(program_uid)
    
    def upsert_connection_settings(self, program_connection: ProgramConnectionBase) -> Any:
        return self.strategy.upsert_connection_settings(program_connection)

   