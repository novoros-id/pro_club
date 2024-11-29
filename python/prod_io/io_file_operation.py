import os
import io_json
import io_universal

def create_user(bot, chat_id, user_name):
    create_folder_structure(user_name)
    io_json.create_file_user_config(user_name)
    bot.send_message(chat_id, "Папки созданы")

def return_user_folder(user_name):
    user_folder_name = io_universal.sanitize_filename(user_name)
    main_folder_path = io_json.get_config_value("main_folder_path")
    return (os.path.join(main_folder_path, user_folder_name))

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
            
