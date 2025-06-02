from fastapi import BackgroundTasks
from typing import Any
from app.models import UserBase
from app.core.provider_db import Provider
import app.utils.io_file_operation as io_file_operation
from app.utils.io_db import DbHelper
import app.utils.response as response_utils
from app.models import SimpleRequest

class FileService:
    def __init__(self):
        pass
    
    async def save_files_and_process(self, 
                                     user: UserBase, 
                                     files: list, 
                                     request: SimpleRequest,
                                     db_provider: Provider,
                                     background_tasks: BackgroundTasks) -> Any:
        saved_files = await self.save_user_files(user, files, request, db_provider)
        background_tasks.add_task(self.process_user_files, request, user, db_provider, saved_files)

    async def save_user_files(self, 
                              user: UserBase, 
                              files: list, 
                              request: SimpleRequest,
                              db_provider: Provider,) -> Any:
        files_list = []
        for file in files:
            filename = file.filename
            file_path = io_file_operation.return_user_folder_input(user)
            with open(f"{file_path}/{filename}", "wb") as buffer:
                buffer.write(file.file.read())
                files_list.append(filename)
        files_str = ', '.join(files_list)

        response_text = f'Файл(ы) {files_str} успешно загружен(ы)! Начинаю обработку файла.\nВ зависимости от размера файла время обработки может увеличиваться.'
        simple_response = response_utils.create_simple_response_from_request(request, response_text)
        response = await response_utils.send_request(simple_response, "upload", db_provider)

        return files_list  # Возвращаем список имен файлов
        
    async def process_user_files(self, 
                                 request: SimpleRequest,
                                 user: UserBase, 
                                 db_provider: Provider,
                                 saved_files = []) -> Any:
        result_processing_files = io_file_operation.copy_user_files_from_input(user)
        db_helper = DbHelper(user)
        db_helper.processing_user_files(None,saved_files)
        print("finish db_helper.processing_user_files()")
        response_text = f'Файл(ы) {result_processing_files["files"]} успешно обработан(ы).'
        simple_response = response_utils.create_simple_response_from_request(request, response_text)
        response = await response_utils.send_request(simple_response, "upload", db_provider)

    async def get_list_files(self, 
                             request: SimpleRequest, 
                             user: UserBase,
                             db_provider: Provider) -> Any:
        list_files = io_file_operation.get_list_user_files(user)
        simple_response = response_utils.create_simple_response_from_request(request, list_files)
        await response_utils.send_request(simple_response, "list_files", db_provider)

    async def delete_all_user_files(self, 
                                    request: SimpleRequest, 
                                    user: UserBase,
                                    db_provider: Provider,
                                    background_tasks: BackgroundTasks) -> Any:
        #Очитка файловой системы
        background_tasks.add_task(io_file_operation.delete_all_files, user)
        #удаление структуры LLM
        db_helper = DbHelper(user)
        background_tasks.add_task(db_helper.delete_all_user_db)
        simple_response = response_utils.create_simple_response_from_request(request, "Файлы удалены")
        response = await response_utils.send_request(simple_response, "delete_files", db_provider)

