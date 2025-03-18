import json
import os
""" import config """

from app.config import settings

""" def get_config_value(key):

    filename = config.path_config_json

    with open(filename, 'r') as file:
        data = json.load(file)
        return data.get(key) """

def get_user_folder(key):
    """
    Возвращает список папок (пользователей) из дериктории указаной в конфиге.
    :key: Ключ указанный в конфиге, содержащий путь к дериктории.
    :return: Список имен папок в указанной дериктории
    """
    try:
        folder_path = get_config_value(key)

        if folder_path and os.path.exists(folder_path):
            return [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
        else:
            raise FileNotFoundError(f'Путь {folder_path} из конфигурации не найден или не существует')
    except Exception as e:
        raise RuntimeError(f'Ошибка при получении списка папок пользователей: {e}')   
    
def create_file_user_config (user_name):
    import io_file_operation
    user_folder_path = io_file_operation.return_user_folder(user_name)
    config_path = os.path.join(user_folder_path, 'config.json')
    
    # Проверяем существование файла
    if not os.path.exists(config_path):
        # Если файла нет, создаем его
        data = {
            "folder_input": "path_to_folder_input",
            "folder_db": "path_to_folder_db",
            "folder_pdf": "path_to_folder_pdf"
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f'Файл {config_path} успешно создан.')
    #else:
    #    print(f'Файл {config_path} уже существует.')