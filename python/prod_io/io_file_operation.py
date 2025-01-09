import os
import io_json
import io_universal
import io_db
#from io_db import DbHelper
import io_send_telegram
import shutil

def create_user(chat_id, user_name):
    create_folder_structure(user_name)
    io_json.create_file_user_config(user_name)
    #print("Папки созданы")

def process_files(chat_id, user_name):
    copy_user_files_from_input(chat_id, user_name)
    db_helper = io_db.DbHelper(chat_id, user_name)
    db_helper.processing_user_files()
    #io_send_telegram.send_telegram_message(chat_id, "Файлы обработаны, можно задавать вопросы")

def copy_user_files_from_input(chat_id, user_name):
    user_folder_input = return_user_folder_input(user_name)
    user_folder_pdf = return_user_folder_pdf(user_name)

    files = os.listdir(user_folder_input)
    
    for file in files:
        if file_is_pdf(file) or file_is_word(file):
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

def get_list_files(chat_id, user_name):
    input_user_files = return_user_folder_input(user_name)
    files = os.listdir(input_user_files)
    result = '\n'.join(files)
    if result == "":
        io_send_telegram.send_telegram_message(chat_id, "Файлы отсутствуют")
    else:
        io_send_telegram.send_telegram_message(chat_id, result)

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
    
def  return_zakroma_folder():  
    main_folder_path = io_json.get_config_value("main_folder_path")
    zakroma_folder = "_zakroma_folder"
    subfolder_path = os.path.join(main_folder_path, zakroma_folder)
    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)
    return subfolder_path

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

def delete_all_files(chat_id, user_name):
    input_user_files = return_user_folder_input(user_name)
    delete_all_files_in_folder(chat_id, input_user_files)

    pdf_user_files = return_user_folder_pdf(user_name)
    copy_files_to_zakroma(pdf_user_files)
    delete_all_files_in_folder(chat_id, pdf_user_files)

    db_helper = io_db.DbHelper(chat_id, user_name)
    db_helper.delete_all_user_db()
    #db_user_files = return_user_folder_db(user_name)
    #delete_all_files_in_folder(chat_id, db_user_files, True)

def delete_all_files_in_folder(chat_id, folder_path, delete_dirs=False):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                io_send_telegram.send_telegram_message(chat_id, "Удален файл - " + file_path)
            elif os.path.isdir(file_path) and delete_dirs:
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Не удалось удалить {filename}: {e}')
  

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

def return_user_folder_db(user_name):
    user_folder_path = return_user_folder(user_name)
    return (os.path.join(user_folder_path, "db"))

def create_folder_structure(user_name):

    # Путь к папке пользователя
    user_folder_path = return_user_folder(user_name)
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
            