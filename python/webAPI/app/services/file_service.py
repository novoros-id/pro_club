from fastapi import HTTPException, status
from typing import Any
import os
import app.utils.io_json as io_json
import app.utils.io_universal as io_universal
from app.config import settings

from app.models import UserRequest


class FileService:

    def create_folder_structure(self, user_name):
        # Путь к папке пользователя
        user_folder_path = self.return_user_folder(user_name)
        #print(user_folder_path)
        
        # Создаем основную папку
        if not os.path.exists(user_folder_path):
            os.makedirs(user_folder_path)
            
        # Создаем подпапки
        subfolders = ["input", "pdf", "db"]
        for subfolder in subfolders:
            subfolder_path = os.path.join(user_folder_path, subfolder)
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path)

    def return_user_folder(self, user_name):
        user_folder_name = io_universal.sanitize_filename(user_name)
        main_folder_path = settings.MAIN_FOLDER_PATH
        return (os.path.join(main_folder_path, user_folder_name))
    
    def return_user_folder_pdf(self, user_name):
        user_folder_path = self.return_user_folder(user_name)
        return (os.path.join(user_folder_path, "pdf"))

    def return_user_folder_input(self, user_name):
        user_folder_path = self.return_user_folder(user_name)
        return (os.path.join(user_folder_path, "input"))

    def return_user_folder_db(self, user_name):
        user_folder_path = self.return_user_folder(user_name)
        return (os.path.join(user_folder_path, "db"))
    
    def get_list_files(self, user: UserRequest) -> Any:
        input_user_files = self.return_user_folder_input(user.name)
        files = os.listdir(input_user_files)
        result = '\n'.join(files)
        if result == "":
            return "Файлы отсутствуют"
        else:
            return result
        """ if result == "":
            io_send_telegram.send_telegram_message(chat_id, "Файлы отсутствуют")
        else:
            io_send_telegram.send_telegram_message(chat_id, result) """

    def file_is_pdf(self, file_path):
        # Получаем расширение файла
        extension = os.path.splitext(file_path)[1]

        if extension.lower() == '.pdf':
            #print('Файл имеет расширение PDF.')
            return True
        else:
            #print('Файл не имеет расширения PDF.')
            return False

    def file_is_word(self, file_path):
        # Получаем расширение файла
        extension = os.path.splitext(file_path)[1]

        if extension.lower() == '.docx':
            #print('Файл имеет расширение Doc.')
            return True
        else:
            #print('Файл не имеет расширения Doc.')
            return False 

    def process_files(self, chat_id, user_name):
        self.copy_user_files_from_input(chat_id, user_name)
        db_helper = io_db.DbHelper(chat_id, user_name)
        db_helper.processing_user_files()
    
    def copy_user_files_from_input(self, chat_id, user_name):
        user_folder_input = self.return_user_folder_input(user_name)
        user_folder_pdf = self.return_user_folder_pdf(user_name)

        files = os.listdir(user_folder_input)
        
        for file in files:
            if self.file_is_pdf(file) or self.file_is_word(file):
            #if file_is_pdf(file):
                source_file_path = os.path.join(user_folder_input, file)
                destination_file_path = os.path.join(user_folder_pdf, file)         
                try:
                    # Перемещаем файл
                    shutil.copy(source_file_path, destination_file_path)
                    print(f"Файл {file} успешно скопирован.")
                except Exception as e:
                    print(f"Ошибка при копировании файла {file}: {e}")
            else:
                io_send_telegram.send_telegram_message(chat_id, "Обрабатываются только файлы в формате docx и pdf файл " + file + " не может быть обработан" )