import config
import telebot
import io_file_operation
import io_db
import os
import shutil
import pandas
import datetime
from threading import Timer
import io_json
import re
import rag_metrick


# ---= КЛАСС ДЛЯ УПРАВЛЕНИЯ ЛОГАМИ =---
class LogManager:
    def __init__(self, logs_folder_path, logs_file_name):
        self.logs_folder_path = logs_folder_path
        self.logs_file_name = os.path.join(logs_folder_path, logs_file_name)
        self.logs = self._initialize_logs()

    def _initialize_logs(self):
        if not os.path.exists(self.logs_folder_path):
            os.makedirs(self.logs_folder_path)
        if not os.path.exists(self.logs_file_name):
            logs = pandas.DataFrame(columns=['request_time', 'chat_id', 'user_name', 'request_text', 'response_time', 'response_text', 'used_files', 'rating'])
            logs.to_csv(self.logs_file_name, index=False, encoding='utf-8')
            return logs    
        # Если файл существует, читаем его    
        try:
            return pandas.read_csv(self.logs_file_name, encoding='utf-8')
        except Exception as e:
            print(f"Ошибка при чтении логов: {e}")
            return pandas.DataFrame(columns=['request_time', 'chat_id', 'user_name', 'request_text', 'response_time', 'response_text', 'used_files', 'rating'])

    # При $start_pipeline создаем отдельный файл с логами
    def create_log_pipeline(self):
        current_time = datetime.datetime.now()
        log_file_name = f'test_pipeline_{current_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        log_file_path = os.path.join(self.logs_folder_path, log_file_name)
        
        try:
            logs = pandas.DataFrame(columns=['request_time', 'chat_id', 'user_name', 'request_text', 'response_time', 'response_text', 'used_files', 'rating'])
            logs.to_csv(self.logs_file_name, index=False, encoding='utf-8')
            self.logs_file_name = log_file_path
        except Exception as e:
            print(f'Ошибка при создании файла тестовых логов: {e}')
            raise

        return log_file_name
    
    #По завершении работы тестового конвейера вернём путь к основному лог файлу
    def switch_to_main_logs(self):
        main_log_file_name = "bot_logs.csv"
        self.logs_file_name = os.path.join(self.logs_folder_path, main_log_file_name)

    def log_rating(self, chat_id, rating):
        # Убедимся, что колонка rating имеет тип object
        if 'rating' in self.logs.columns and self.logs['rating'].dtype != 'object':
            self.logs['rating'] = self.logs['rating'].astype('object')

        # Обновляем запись в логах, по соответствующему chat_id
        if not self.logs.empty:
            # Находим последнюю запись в логах для этого chat_id
            self.logs.loc[self.logs['chat_id'] == chat_id, 'rating'] = rating
            
        # Сохраняем логи
        try:
            self.logs.to_csv(self.logs_file_name, index=False, encoding='UTF-8')
        except Exception as e:
            print(f'Ошибка при сохранении логов: {e}')

    def log_interaction(self, request_time, chat_id, user_name, request_text, response_time, response_text, used_files_path, rating=None):
        used_files_str = ", ".join(os.listdir(used_files_path)) if os.path.exists(used_files_path) else "Папка не создана"

        # Создаем запись логов
        new_array = pandas.DataFrame([{
            'request_time'  : request_time,
            'chat_id'       : chat_id,
            'user_name'     : user_name,
            'request_text'  : request_text,
            'response_time' : response_time,
            'response_text' : response_text,
            'used_files'    : used_files_str,
            'rating'        : rating
        }])

        if self.logs.empty:
            self.logs = new_array
        else:
            self.logs = pandas.concat([self.logs, new_array], ignore_index=True)

        try:
            self.logs.to_csv(self.logs_file_name, index=False, encoding='utf-8')
        except Exception as e:
            print(f'Ошибка при создании логов: {e}')

# ---= КЛАСС ОБРАБОТКИ ДАННЫХ ДЛЯ ТЕСТ-КОНВЕЙЕРА =---
class TestPipeline:
    def __init__(self):
        self.unique_source_files = []
    
    def initialize_files(self, source_data):
        
        #Инициализация файла источника данных
        self.unique_source_files = source_data
        print(f'Инициализирован файл: {self.unique_source_files}')
    
    def validate_files(self, uploaded_files):

        #Проверка что все необходимые файлы для запуска тестового конвейера загружены
        missing_files = set(self.unique_source_files) - set(uploaded_files)
        if missing_files:
            print(f'Отсутствуют файлы: {missing_files}')
        else:
            print('Все необходимые файлы найдены')

    def process_files(self):

        #Обработка файлов из списка unique_source_files
        for file_name in self.unique_source_files:
            print(f'Обрабатывается файл: {file_name}')

# ---= ИНИЦИАЛИЗАЦИЯ БОТА =---
logs_folder_path = io_json.get_config_value('logs_folder_path')
logs_manager = LogManager(logs_folder_path, 'bot_logs.csv')
task_for_test_folder = io_json.get_config_value('task_for_test')
bot = telebot.TeleBot(config.bot_token)
user_context = {}

HELP_BUTTON = 'Помощь'
FILES_LIST_BUTTON = 'Загруженные файлы'
DELETE_FILES_BUTTON = 'Удалить все загруженные файлы'

# ---= ОБРАБОТКА КОМАНД =---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    username = message.from_user.username or 'Unknown_user'
    first_name = message.from_user.first_name
    io_file_operation.create_user(chat_id, username)

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        telebot.types.KeyboardButton(text=HELP_BUTTON),
        telebot.types.KeyboardButton(text=FILES_LIST_BUTTON),
        telebot.types.KeyboardButton(text=DELETE_FILES_BUTTON),
    )

    bot.send_message(message.chat.id,
        f"""Привет, {first_name}! Я бот помощник. Я помогу тебе найти нужный ответ
        Отправь мне файлы в формате PDF или DOCX и задавай по ним вопросы
        Если хочешь пообщаться не по текстам, то отправь мне сообщение которое начинается с [$]
        Если у тебя будут предложения обращайся в Клуб Разработчиков 1С ПРО Консалтинг \n\n"""
        , reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
def help_bot(message):
    chat_id = str(message.chat.id)
    username = message.from_user.username
    io_file_operation.create_user(chat_id, username)
    bot.send_message(message.chat.id, 
        f'Вот что я умею:\n\n'
        f'1️⃣  {FILES_LIST_BUTTON} - позволяет получить перечень загруженных файлов\n'
        f'2️⃣  {DELETE_FILES_BUTTON} - выполняет полное удаление всех загруженных ранее файлов'
    )

#  --= ТЕСТОВЫЙ КОНВЕйЕР =---
#Создание тестового пользователя
def create_test_user_for_pipeline(chatID):

# Создадим тестового пользователя
    test_username = 'test_user_pipeline'

    users = io_json.get_user_folder('main_folder_path')

    # Проверяем есть ли тестовый пользователь
    if isinstance(users, list) and test_username not in users: #Думается, что в дальнейшем надо проверку переделать на ChatID

        # Создаем пользователя если его нет
        if io_file_operation.create_user(chatID, test_username):
            bot.send_message(chatID, f'Создан пользователь: {test_username} для запуска тестового конвейера')
        else:
            bot.send_message(chatID, f'Ошибка создания пользователя: {test_username}')
        
    # Если пользователь есть продолжаем работу конейера от его имени
    bot.send_message(chatID, f'Тест-конвейер запускается от пользователя: {test_username}')

# Функция чтения файла для тестов
def read_test_excel_file (file_name):
    if not os.path.exists(task_for_test_folder):
        os.makedirs(task_for_test_folder)

    file_path = os.path.join(task_for_test_folder, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл '{file_name}' отсутствует в папке '{task_for_test_folder}'.")
    
    try:
        data_frame = pandas.read_excel(file_path)
    except Exception as e:
        raise ValueError(f'Ошибка при чтении Excel-файла: {e}')
    
    if data_frame is None or data_frame.empty:
        raise ValueError('Excel-файл пуст или не содержит данных')
    
    required_columns = {'request_text', 'response_text', 'Source'} #TODO проверку нужно переписать с учетом def validate_file_structure
    if not required_columns.issubset(data_frame.columns):
        raise ValueError(f'Отсутствуют необходимые колонки в файле: {required_columns - set(data_frame)}')
    
    return data_frame

# Функция для обработки загруженных файлов
def handle_uploaded_file(message):
    chatID = message.chat.id

    print("Ничинаю загрузку файла")

    # Проверяем, отправил ли пользователь файл
    if not message.document:
        bot.send_message(chatID, 'Ошибка: Файл можно загрузить после команды $update_prime')
        return

    file_name = message.document.file_name
    file_size = message.document.file_size

    # Проверка имени файла
    if file_name != 'prime.xlsx':
        bot.send_message(chatID, 'Бот ожидает файл prime.xlsx')
        return
    
    # Проверка размера файла
    if file_size > 50 * 1024 * 1024: # 50 MB
        bot.send_message(chatID, 'Размер файла не должен превышать 50 Мб')
        return

    # Загружаем файл
    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохраняем временный файл
    temp_file_path = f"E:\\temp\\folder_io_project\\task_for_test{file_name}"
    with open(temp_file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    # Проверка содержимого файла
    if not validate_file_structure(temp_file_path):
        os.remove(temp_file_path) #удаляем временный файл
        bot.send_message(chatID, "Ошибка: Файл должен содержать колонки 'request_text', 'response_text', 'Source'")
        return
    
    # Обновляем файл 
    update_prime_file(temp_file_path, chatID)

# Функция проверки нужных колонок при загрузки файла
def validate_file_structure(file_path):
    try:
        df = pandas.read_excel(file_path)
        required_columns = {'request_text', 'response_text', 'Source'}
        return required_columns.issubset(df.columns)
    except Exception as e:
        return False

# Функция для обновления файла prime.xlsx
def update_prime_file(temp_file_path, chatID):
    try:
        task_folder = io_json.get_config_value('task_for_test')
        zakroma_folder = io_file_operation.return_zakroma_folder()

        prime_path = os.path.join(task_folder, 'prime.xlsx')
        if os.path.exists(prime_path):
            # Перемещаем старый файл в архив
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            archive_name = f'prime_{timestamp}.xlsx'
            shutil.move(prime_path, os.path.join(zakroma_folder, archive_name))
            bot.send_message(chatID, f'Предыдущий файл перемещен в zakroma_folder под именем {archive_name}')
        
        # Перемещаем новый файл
        shutil.move(temp_file_path, prime_path)
        bot.send_message(chatID, 'Файл успешно обновлен')
    except Exception as e:
        bot.send_message(chatID, f'Ошибка при обновлении файла: {str(e)}')
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Универсальная обработка колонок
def process_column(data_frame, column_name, description, chatID, send_message=False):

    if column_name in data_frame.columns:
        values = data_frame[column_name].dropna().unique().tolist()
        values = [str(value).strip() for value in values] #Преобразование в строку

        if send_message:
            result_text = '\n'.join(values)
            response_text = f'{description}:\n{result_text}'
            bot.send_message(chatID, response_text)

        return values
    else:
        bot.send_message(chatID, f'Колонка "{column_name}" в файле отсутствует')
        return None

# Функция получения списка файлов для тест-конвейера
def initialize_pipeline_source(chatID, excel_lile="prime.xlsx", send_message=False):
    
    #Загружаем данные из Excel
    try:
        test_data = read_test_excel_file(excel_lile)
    except FileNotFoundError:
        bot.send_message(chatID, 'Файл prime.xlsx не найден. Проверьте наличие файла')
        return False
        
    # Обработка колонки 'Source'
    unique_sources  = process_column(
        data_frame  = test_data,
        column_name = 'Source',
        description = 'Следующие файлы из колонки "Source" будут использоваться в тестах',
        chatID      = chatID,
        send_message= send_message
    )

    unique_sources = [source.strip() for source in unique_sources if isinstance(source, str) and source.strip()]
    if not unique_sources:
        bot.send_message(chatID, 'Не корректные данные в колонке "Source"')
        return False

    # Возвращаем список уникальных файлов
    return unique_sources

# Формирование базы данных с файлами для тестового пользователя
def simulate_upload_for_test_user(chatID):
    zakroma_folder = io_file_operation.return_zakroma_folder()

    # Инициализация pipeline через общую функцию
    unique_sources = initialize_pipeline_source(chatID, send_message=True)
    if unique_sources is None:
        return False

    pipeline = TestPipeline()
    pipeline.initialize_files(unique_sources)

    # Папка для файлов тестового пользователя
    test_username = 'test_user_pipeline'
    user_input_folder = io_file_operation.return_user_folder_input(test_username)

    # Создаем папку тестового пользователя, если её нет
    if not os.path.exists(user_input_folder):
        os.makedirs(user_input_folder)
    
    # Копируем файлы из zakroma_folder в папку тестового пользователя
    for file_name in pipeline.unique_source_files:
        source_file_path = os.path.join(zakroma_folder, file_name)
        destination_file_path = os.path.join(user_input_folder,file_name)

        if os.path.exists(source_file_path):

            try:
                if not os.path.exists(destination_file_path):
                    shutil.copy(source_file_path, destination_file_path)
                    print(f'Файл {file_name} успешно скопировать в папку тестового пользователя')

            except Exception as e:
                print (f'Ошибка при копировании файла {file_name}: {e}')

        else:
            print(f'Файл {file_name} отсутствует в папке {zakroma_folder}')
            return False # Если хотя бы одного файла нет, возвращаем False
    
    # Имитируем загрузку файлов тестовым пользователем
    for file_name in pipeline.unique_source_files:
        file_path = os.path.join(user_input_folder, file_name)

        if os.path.exists(file_path):

            # Обрабатываем файл как будто он был загружен пользователем
            bot.send_message(chatID, f'Запустили загрузку файлов. Нужно подождать...')
            io_file_operation.process_files(chatID, test_username)  

        else:
            print(f'Файл {file_name} отсутствует в папке {user_input_folder}')
            return False
    
    bot.send_message(chatID, 'Все файлы успешно обработаны')
    return True

# Функция обработки команды $start_pipeline
def handle_start_pipeline(chatID):
    logs_folder_path_pipeline = io_json.get_config_value('task_for_test')
    current_time = datetime.datetime.now()
    logs_file_name_pipeline = f'test_pipeline_{current_time.strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    logs_manager_pipeline = LogManager(logs_folder_path_pipeline, logs_file_name_pipeline)
    max_telegram_message_length = 3800 # На самом деле максимально телега в одно сообщение может уместить 4096, но я уменьшил с запасом
    test_username = 'test_user_pipeline'

    # Обрезает текст, если он превышает mmax_length, добавляя '...' в концу
    def truncate_text(text, max_length=max_telegram_message_length):
        return text if len(text) <=max_length else text[:max_length] + "..."


    try:
        #Загружаем данные из Excel
        try:
            test_data = read_test_excel_file("prime.xlsx")
        except FileNotFoundError:
            bot.send_message(chatID, 'Файл prime.xlsx не найден. Проверьте наличие файла')

        # Обработка колонки 'Question'   
        test_questions  = process_column(
            data_frame  = test_data,
            column_name = 'request_text',
            description = f'Следующие вопросы из колонки "request_text" будут использоваться в тестах',
            chatID      = chatID
        )

        if not test_questions or not isinstance(test_questions, list):
            bot.send_message(chatID, 'Вопросы из колонки "request_text" отсутствуют или не найдены')
            return
        
        # Если вопросы найдены, обработаем их
        total_questions = len(test_questions)

        # Создание лог-файла
        #log_file_name = logs_manager.create_log_pipeline()
        bot.send_message(chatID, f'Создан лог-файл: {logs_file_name_pipeline}')

        # Подготовка объекта db_helper для тестового пользователя
        db_helper = io_db.DbHelper(chatID, user_name=test_username)
        used_files_path = io_file_operation.return_user_folder_pdf(test_username)
        # Поочередная обработка вопросов
        for idx, question in enumerate(test_questions, start=1):

            # Обрезаем текст вопроса, если он слишком длинный
            truncated_question = truncate_text(question)

            # Отправляем вопрос и получаем ответ
            bot.send_message(chatID, f"Вопрос {idx} из {total_questions} отправлен от имени {test_username}. Текст вопроса: {truncated_question}")
            print(f'[DEBUG] Отправляем вопрос: {truncated_question}')

            # Получаем ответ
            response = db_helper.get_answer(prompt=question)

            # Обрезаем ответ, если он слишком длинный
            truncated_response = truncate_text(response)
            print(f'[DEBUG] Ответ содержит: {truncated_response}')

            # Запись в лог
            logs_manager_pipeline.log_interaction(
                request_time    = datetime.datetime.now(),
                chat_id         = chatID,  
                user_name       = test_username, # Лог пишется от имени test_user_pipeline
                request_text    = question,
                response_time   = datetime.datetime.now(),
                response_text   = response,
                used_files_path = used_files_path,
                rating          = None
            )

            # Обновляем прогресс
            bot.send_message(chatID, f"Получен ответ на {idx} из {total_questions} вопросов. Ответ: {truncated_response} ")

        # Сообщаем о завершении
        bot.send_message(chatID, "Все вопросы успешно обработаны. Логи записаны.")
        bot.send_message(chatID, "Запускаю подсчет метрик.")

        # Вызов метрик
        prime_file_path = os.path.join(task_for_test_folder, "prime.xlsx")
        log_path_file_name = os.path.join(logs_folder_path_pipeline, logs_file_name_pipeline)
        file_metrick_ = metrick_start(chatID, task_for_test_folder, log_path_file_name, prime_file_path)
        doc = open(file_metrick_, 'rb')
        bot.send_document(chatID, doc)
        #bot.send_document(chatID, open(r'Путь_к_документу/Название_документа.txt, 'rb'))

        # Переключаемся на основной лог-файл
        #logs_manager.switch_to_main_logs()

    except FileNotFoundError as fnf_error:
        bot.send_message(chatID, str(fnf_error))

    except Exception as e:
        bot.send_message(chatID, f'Ошибка при запуске конвейера: {e}')

# Функция обработки RAG метрик
def metrick_start (chatID, task_for_test_folder, log_file_name, prime_file_path):
    metrick = rag_metrick.rag_metrick(task_for_test_folder, log_file_name, prime_file_path)
    try:
        file_metrick = metrick.gmetrics()
        bot.send_message(chatID, f'Файл метрик: {file_metrick}')
        return file_metrick
    except:
        bot.send_message(chatID, f'Возникла ошибка при обработке метрик, проверьте пожалуйста: {file_metrick}')
        return file_metrick  

# ---= ОБРАБОТКА ТЕКСТОВЫХ КОМАНД =---
@bot.message_handler(content_types=['text'])
def handle_buttons(message):
    text = message.text.strip()
    chatID = message.chat.id
    username = message.from_user.username
    io_file_operation.create_user(chatID, username)
    request_time = datetime.datetime.now()
    input_user_files = io_file_operation.return_user_folder_input(username)

    if text.startswith ('$get_user'):
        try:
            users = io_json.get_user_folder("main_folder_path")
            if isinstance(users, list) and users:
                response_text = f'Список доступных пользователей:\n{chr(10).join(users)}'

            else:
                response_text = 'Нет доступных пользователей'
        except Exception as e:
            response_text = f'Ошибка при получении списка пользователей: {e}'
        bot.send_message (chatID, response_text)

    elif text.startswith ('$start_pipeline'):
        # 1. Инициализируем тестового пользователя
        create_test_user_for_pipeline(chatID)
       
        # 2. Проверяем наличие нужных для тест-конвейера файлов, загруженных в базу у тестового пользователя
        # Если нужных файлов нет, тогда все имеющиеся файлы будут удалены, а нужные будут загружены из zakroma_folder
        test_username = 'test_user_pipeline'
        pipeline = TestPipeline()

        # Получаем список файлов тестового пользователя
        uploaded_files = io_file_operation.get_list_files_for_pipeline(chatID, test_username)
        unique_sources = initialize_pipeline_source(chatID)
        if unique_sources is None:
            return
        
        pipeline.initialize_files(unique_sources)

        # Если есть необходимые файлы запускаем конвейер
        if uploaded_files is None:
            # Если список файлов пуст
            bot.send_message(chatID, 'Файлы для запуска не найдены. Пытаемся загрузить необходимые файлы...')
            try:
                if not simulate_upload_for_test_user(chatID):
                    bot.send_message(chatID, f'Ошибка: не удалость загрузить необходимые файлы для конвейера. Конвейер прерван')
                    return

            except Exception as e:
                bot.send_message(chatID, f'Ошибка при загрузке файлов: {e}')
                return

        elif set(pipeline.unique_source_files).issubset(set(uploaded_files)):
            # Если файлы найдены
            bot.send_message(chatID, 'Файлы успешно найдены. Запусткаем тест-конвейер.')
            # Переходим к "3. Запуск тест-конвейера"

        else:
            # Если файлы отсутствуют 
            bot.send_message(chatID, "Файлы для запуска не найдены. Перезагружаем базу пользователя")
            io_file_operation.delete_all_files(chatID, test_username)
            bot.send_message(chatID, "Пытаемся загрузить необходимые файлы...")
            try:
                simulate_upload_for_test_user(chatID)
            except Exception as e:
                bot.send_message(chatID, f'Ошибка при загрузке файлов: {e}')
                return

            #После успешной загрузки выполняем повторную проверку наличия необходимых файлов
            uploaded_files = io_file_operation.get_list_files_for_pipeline(chatID, test_username)
            if set(pipeline.unique_source_files).issubset(set(uploaded_files)):
                bot.send_message(chatID, 'Файлы успешно найдены. Запусткаем тест-конвейер.')
                # Переходим к "3. Запуск тест-конвейера"
                
            else:
                bot.send_message(chatID, f'Не удалость найти для запуска тест-конвейера следующие файлы: {pipeline.unique_source_files}\nПопытки запуска тест-конвейера остановлены')
        
        # 3. Запуск тест-конвейера
        handle_start_pipeline(chatID)

    elif re.match(r'\$(\w+)\s(.+)', text):
        try:
            match = re.match(r'\$(\w+)\s(.+)', text)
            
            substitution_user_id = match.group(1) # user_id другого пользователя
            substitution_query =  match.group(2) # Запрос, который задаем от другого пользователя

            # Обрабатываем запрос от другого пользователя
            db_helper = io_db.DbHelper(chat_id=substitution_user_id, user_name=substitution_user_id)
            #TODO Переделать на user_id когда будет поправлена процедура DbHelper
            #db_helper = io_db.DbHelper(chat_id=substitution_user_id)
            answer = db_helper.get_answer(prompt=substitution_query)

            bot.send_message(chatID, f'Запрос от имени пользователя: {substitution_user_id}: \n {substitution_query}\n\Ответ: {answer}')
        except Exception as e:
            bot.send_message(chatID, f'Произошла ошибка: {e}')
            print(f'Ошибка в обработке от имени другого пользователя: {e}')
        return
    
    elif text == HELP_BUTTON:    
        help_bot(message)

    elif text.startswith ('$help'):
        bot.send_message(chatID, 'Доступные сервисные команды:\n$start_pipeline\n$get_user')

    elif text == FILES_LIST_BUTTON:
        io_file_operation.get_list_files(chatID, username)

    elif text == DELETE_FILES_BUTTON:
        io_file_operation.delete_all_files(chatID, username)

    else:
        if not text.strip():
            response_text = (chatID, 'Извините, необходимо указать запрос!')
            bot.send_message(chatID, response_text)

        elif text.startswith ('$'):
            bot.send_message(chatID, 'Запрос не по текстам. Подготовка ответа может занять некоторое время...')
            db_helper = io_db.DbHelper(chat_id=chatID, user_name=username)
            response_text = db_helper.get_free_answer(prompt=text)
            bot.send_message(chatID, response_text)

        else:
            bot.send_message (chatID, 'Запрос к загруженным текстам, это тестовый сервер и для ответа необходимо более одной минуты. Вы можете перейти к другим задачам, а когда я буду готов, то Вам придет оповещение')
            try:
                db_helper = io_db.DbHelper(chat_id=chatID, user_name=username)
                answer = db_helper.get_answer(prompt=text)
                if answer:
                    response_text = f'Ответ: {answer}\n\n Пожалуйста, оцените качество ответа:'

                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
                    keyboard.add(
                        telebot.types.InlineKeyboardButton('👍', callback_data=f'rate_{chatID}_up'),
                        telebot.types.InlineKeyboardButton('👎', callback_data=f'rate_{chatID}_down')
                    )
                    bot.send_message(chatID, response_text, reply_markup=keyboard)
                    #Логируем действия
                    logs_manager.log_interaction(
                        request_time    =request_time,
                        chat_id         =chatID,
                        user_name       =username,
                        request_text    =text,
                        response_time   =datetime.datetime.now(),
                        response_text   =response_text,
                        used_files_path =input_user_files,
                        rating          =None
                    )

                else:
                    response_text = 'Извините, я не смог сформировать ответ!'
                    bot.send_message(chatID, response_text)
            except Exception as e:
                response_text = 'Произошла ошибка при обработке запроса.'
                bot.send_message(chatID, response_text)
                print(f'Ошибка в get_answer: {e}')

# ---= ОБРАБОТКА ДОКУМЕТОВ =---
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chatID = message.chat.id
    username = message.from_user.username
    io_file_operation.create_user(chatID, username)
    file_info = bot.get_file(message.document.file_id)
    file_name = message.document.file_name

    if file_name == "prime.xlsx":
        print ("Загрузка файла prime.xlsx")
        # Загружаем файл
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем временный файл
        temp_file_path = f"E:\\temp\\folder_io_project\\task_for_test{file_name}"
        with open(temp_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Проверка содержимого файла
        if not validate_file_structure(temp_file_path):
            os.remove(temp_file_path) #удаляем временный файл
            bot.send_message(chatID, "Ошибка: Файл должен содержать колонки 'request_text', 'response_text', 'Source'")
            return
        
        # Обновляем файл 
        update_prime_file(temp_file_path, chatID)
    else:
        dowloaded_file = bot.download_file(file_info.file_path)
        user_input_folder = io_file_operation.return_user_folder_input(username)
        save_path = os.path.join(user_input_folder, file_name)
        
        with open(save_path, 'wb') as new_file:
            new_file.write(dowloaded_file)

        bot.send_message(chatID, f"Файл '{file_name}' успешно загружен! Начинаю обработку файла.\nВ зависимости от размера файла время обработки может увеличиваться")
        io_file_operation.process_files(chatID, username)
        bot.send_message(chatID, f"Файл '{file_name}' успешно обработан")

# ---= ОБРАБОТКА НЕПОДДЕРЖИВАЕМЫХ ДОКУМЕТОВ =---
@bot.message_handler(content_types=['photo', 'audio', 'video', 'voice', 'sticker', 'animation', 'video_note'])
def handle_unsupported_files(message):
    bot.send_message(message.chat.id, "Извините, я обрабатываю только текстовые документы (например PDF, TXT или DOC). Пожалуйста, отправьте корректный формат файла")

# ---= ОБРАБОТКА ОЦЕНКИ ОТВЕТОВ =---
@bot.callback_query_handler(func=lambda call: call.data.startswith('rate_'))
def handle_rating(call):
    # Получаем данные из callback_data
    _, chat_id, rating = call.data.split('_')  #Например, rate_12321321_up
    chat_id = int(chat_id)
    rating_value = '👍' if rating == 'up' else '👎'

    logs_manager.log_rating(chat_id=chat_id, rating=rating_value)

    bot.answer_callback_query(call.id, f'Вы выбрали оценку:{rating_value}')

# ---= ЗАПУСК БОТА =---
try:
    print("БОТ ЗАПУЩЕН!")
    bot.polling(none_stop=True, interval=1)
except Exception as e:
    # Информация об ошибке 
    print(f"Ошибка:{e}")
finally:
    bot.stop_polling()
    print("БОТ ОСТАНОВЛЕН")