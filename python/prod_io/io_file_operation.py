import os
import io_json
import io_universal
import io_send_telegram
import io_db
import shutil

def copy_user_files_from_input_pdf(user_name):
    user_folder_input = return_user_folder_input(user_name)
    user_folder_pdf = return_user_folder_pdf(user_name)

    files = os.listdir(user_folder_input)
    
    for file in files:
        source_file_path = os.path.join(user_folder_input, file)
        destination_file_path = os.path.join(user_folder_pdf, file)
        
        try:
            # Перемещаем файл
            shutil.copy(source_file_path, destination_file_path)
            print(f"Файл {file} успешно скопирован.")
        except Exception as e:
            print(f"Ошибка при копировании файла {file}: {e}") 

def process_files(chat_id, user_name):
    copy_user_files_from_input_pdf(user_name)
    io_db.processing_user_files(chat_id, user_name)


def create_user(chat_id, user_name):
    create_folder_structure(user_name)
    io_json.create_file_user_config(user_name)
    io_send_telegram.send_telegram_message(chat_id, "Пользователь зарегестрирован")

def return_user_folder(user_name):
    user_folder_name = io_universal.sanitize_filename(user_name)
    main_folder_path = io_json.get_config_value("main_folder_path")
    return (os.path.join(main_folder_path, user_folder_name))

def return_user_folder_pdf(user_name):
    user_folder_path = return_user_folder(user_name)
    return (os.path.join(user_folder_path, "pdf"))

def return_user_folder_input(user_name):
    user_folder_path = return_user_folder(user_name)
    return (os.path.join(user_folder_path, "input"))

def create_folder_structure(user_name):

    # Путь к папке пользователя
    user_folder_path = return_user_folder(user_name)
    print(user_folder_path)
    
    # Создаем основную папку
    if not os.path.exists(user_folder_path):
        os.makedirs(user_folder_path)
    
    # Создаем подпапки
    subfolders = ["input", "pdf", "db"]
    for subfolder in subfolders:
        subfolder_path = os.path.join(user_folder_path, subfolder)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
            
