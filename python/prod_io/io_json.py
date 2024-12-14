import json
import os

def get_config_value(key):
    filename = "E:\\Клуб разработчиков\\VS\\pro_club\\python\\prod_io\\config.json"
    with open(filename, 'r') as file:
        data = json.load(file)
        return data.get(key)
    
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
    else:
        print(f'Файл {config_path} уже существует.')