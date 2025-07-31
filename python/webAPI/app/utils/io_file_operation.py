from typing import Any
import os
import shutil
import json
import threading
import app.utils.io_universal as io_universal
from app.config import settings

from app.models import UserBase

# Лимиты в байтах
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 МБ
MIN_FILE_SIZE = 1  # Минимум 1 байт (чтобы исключить 0-байт файлы)

# Глобальные переменные для кэша
_connection_settings_file_cache = None
_cache_lock = threading.Lock()

def create_folder_structure(user: UserBase):
    # Путь к папке пользователя
    user_folder_path = return_user_folder(user)
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

def return_user_folder(user: UserBase):
    user_folder_name = io_universal.sanitize_filename(user.name)
    main_folder_path = settings.MAIN_FOLDER_PATH
    return (os.path.join(main_folder_path, user_folder_name))

def return_user_folder_pdf(user: UserBase):
    user_folder_path = return_user_folder(user)
    return (os.path.join(user_folder_path, "pdf"))

def return_user_folder_input(user: UserBase):
    user_folder_path = return_user_folder(user)
    result = os.path.join(user_folder_path, "input")
    return result

def return_user_folder_db(user: UserBase):
    user_folder_path = return_user_folder(user)
    return (os.path.join(user_folder_path, "db"))

def get_list_user_files(user: UserBase) -> str:
    input_user_files = return_user_folder_input(user)
    files = os.listdir(input_user_files)
    result = '\n'.join(files)
    if result == "":
        return "Файлы отсутствуют"
    else:
        return result

def file_is_pdf(file_path):
    # Получаем расширение файла
    extension = os.path.splitext(file_path)[1]

    if extension.lower() == '.pdf':
        #print('Файл имеет расширение PDF.')
        return True
    else:
        #print('Файл не имеет расширения PDF.')
        return False

def file_is_word(file_path):
    # Получаем расширение файла
    extension = os.path.splitext(file_path)[1]

    if extension.lower() == '.docx':
        #print('Файл имеет расширение Doc.')
        return True
    else:
        #print('Файл не имеет расширения Doc.')
        return False 

def file_is_pptx(file_path):
    # Получаем расширение файла
    extension = os.path.splitext(file_path)[1]

    if extension.lower() == '.pptx':
        #print('Файл имеет расширение pptx.')
        return True
    else:
        #print('Файл не имеет расширения pptx.')
        return False 

def delete_all_files(user: UserBase):
    input_user_files = return_user_folder_input(user)
    delete_all_files_in_folder(input_user_files)

    pdf_user_files = return_user_folder_pdf(user)
    copy_files_to_zakroma(pdf_user_files)
    delete_all_files_in_folder(pdf_user_files)

    #db_helper = io_db.DbHelper(user_name)
    #db_helper.delete_all_user_db()


def delete_all_files_in_folder(folder_path, delete_dirs=False):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                #io_send_telegram.send_telegram_message(chat_id, "Удален файл - " + file_path) todo: Нужно вернуть ответ 
            elif os.path.isdir(file_path) and delete_dirs:
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Не удалось удалить {filename}: {e}')

def copy_files_to_zakroma(folder_source):
    zakroma_folder = return_zakroma_folder()

    files = os.listdir(folder_source)
    
    for file in files:
        source_file_path = os.path.join(folder_source, file)
        destination_file_path = os.path.join(zakroma_folder, file)         
        try:
            # Перемещаем файл
            shutil.copy(source_file_path, destination_file_path)
            print(f"Файл {file} успешно скопирован.")
        except Exception as e:
            print(f"Ошибка при копировании файла {file}: {e}")

def return_zakroma_folder():  
    main_folder_path = settings.MAIN_FOLDER_PATH
    zakroma_folder = "_zakroma_folder"
    subfolder_path = os.path.join(main_folder_path, zakroma_folder)
    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)
    return subfolder_path

def copy_user_files_from_input(user: UserBase) -> dict:
    """
    Копирует PDF, DOCX, PPTX файлы из папки пользователя, 
    пропуская пустые (0 байт) и слишком большие (>20 МБ) файлы.
    """
    result = {
        "result": True,
        "files": [],
        "message": []  # Исправлено опечатку: "mesaage" → "message"
    }

    user_folder_input = return_user_folder_input(user)
    user_folder_pdf = return_user_folder_pdf(user)

    print(f"Папка для входящих файлов: {user_folder_input}")
    print(f"Папка для PDF: {user_folder_pdf}")

    # Проверяем, существует ли папка с входящими файлами
    if not os.path.exists(user_folder_input):
        result["result"] = False
        result["message"].append(f"Папка входящих файлов не существует: {user_folder_input}")
        return result

    if not os.path.exists(user_folder_pdf):
        os.makedirs(user_folder_pdf, exist_ok=True)
        print(f"Создана папка для PDF: {user_folder_pdf}")

    try:
        files = os.listdir(user_folder_input)
    except Exception as e:
        result["result"] = False
        result["message"].append(f"Ошибка при чтении папки {user_folder_input}: {e}")
        return result

    for file in files:
        source_file_path = os.path.join(user_folder_input, file)

        # Пропускаем, если это не файл (например, подпапка)
        if not os.path.isfile(source_file_path):
            continue

        # Проверка расширения
        if not (file_is_pdf(file) or file_is_word(file) or file_is_pptx(file)):
            result["message"].append(f"Пропущен файл: {file} — формат не поддерживается (только pdf, docx, pptx)")
            result["result"] = False  # Можно считать частичный успех, но помечаем, что были ошибки
            continue

        # Получаем размер файла
        try:
            file_size = os.path.getsize(source_file_path)
        except Exception as e:
            result["message"].append(f"Не удалось определить размер файла {file}: {e}")
            result["result"] = False
            continue

        # Проверка размера
        if file_size == 0:
            result["message"].append(f"Пропущен файл: {file} — файл пустой (0 байт)")
            result["result"] = False
            continue

        if file_size > MAX_FILE_SIZE:
            result["message"].append(f"Пропущен файл: {file} — размер {file_size} байт превышает лимит в 20 МБ")
            result["result"] = False
            continue

        # Копируем файл
        destination_file_path = os.path.join(user_folder_pdf, file)
        try:
            shutil.copy(source_file_path, destination_file_path)
            print(f"Файл {file} успешно скопирован.")
            result["files"].append(file)
        except Exception as e:
            print(f"Ошибка при копировании файла {file}: {e}")
            result["result"] = False
            result["message"].append(f"Ошибка при копировании файла {file}: {e}")

    return result

def get_database_config(program_uid):
    #Возвращает конфигурацию базы, лениво загружая JSON при первом вызове.
    load_database_config()  # Проверяем, загружен ли кэш
    return _connection_settings_file_cache.get(program_uid, None)

def load_database_config():
    #Загружает JSON в память, если он еще не загружен
    global _connection_settings_file_cache
    if _connection_settings_file_cache is None:  # Ленивая загрузка
        with _cache_lock:
            if _connection_settings_file_cache is None:  # Повторная проверка (чтобы исключить race condition)
                try:
                    with open(settings.CONNECTION_FILE_PATH, "r", encoding="utf-8") as file:
                        _connection_settings_file_cache = json.load(file)
                except () as e:
                    print(f"Ошибка при загрузке JSON: {e}")
                    _connection_settings_file_cache = {}

def reload_database_config():
    #Принудительно обновляет кэш (если JSON изменился).
    global _connection_settings_file_cache
    with _cache_lock:
        _connection_settings_file_cache = None  # Сбрасываем кэш
    load_database_config()  # Перезагружаем данн