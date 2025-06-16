import telebot
import threading
import uvicorn
from fastapi import FastAPI
from config import settings
import request  # должен быть синхронным!
from models import SimpleResponse
import os
import tempfile
import mimetypes
from concurrent.futures import ThreadPoolExecutor
import time
import pandas
import datetime

# === Инициализация ===
app = FastAPI()
bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
chat_id = -1002719784241

# Словарь для хранения данных запросов
request_chat_map = {}

# История запросов по chat_id
user_history = {}

# Объект для выполнения фоновых задач
executor = ThreadPoolExecutor(max_workers=3)

max_telegram_message_length = 3800

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

# Обрезает текст, если он превышает mmax_length, добавляя '...' в концу
def truncate_text(text, max_length=max_telegram_message_length):
    return text if len(text) <=max_length else text[:max_length] + "..."

@app.post("/process")
def process_request(data: SimpleResponse):
    request_id = data.code_uid.request_uid
    entry = request_chat_map.get(request_id)

    if entry:
        chat_id = entry["chat_id"]
        answer = data.answer
        query_text = entry["query_text"]
        message_id = entry["message_id"]
        user_name = entry["username"]
        request_time = entry["timestamp"]

        # Сохраняем ответ и обновляем статус
        entry["response"] = answer
        entry["status"] = "completed"

        # Добавляем в историю пользователя
        if chat_id not in user_history:
            user_history[chat_id] = []
        user_history[chat_id].append({
            "request_uid": request_id,
            "query": query_text,
            "response": answer,
            "timestamp": time.time(),
            "sources": getattr(data, "sources", [])
        })
        # Формируем текст ответа
        response_text = truncate_text(answer)
        sources = getattr(data, "sources", None)

        # Запись в лог
        logs_manager.log_interaction(
            request_time    =request_time,
            chat_id         =chat_id,
            user_name       =user_name,
            request_text    =query_text,
            response_time   =datetime.datetime.now(),
            response_text   =response_text,
            used_files_path ="None",
            rating          =None
            )

        if sources:
            response_text += "\n\nИсточники:\n" + "\n".join([f"- {s}" for s in sources])

        try:
            bot.send_message(
                chat_id=chat_id,
                text=response_text,
                reply_to_message_id=message_id  # <-- делаем reply
            )
        except Exception as e:
            print(f"[ERROR] При отправке сообщения: {e}")
    else:
        print(f"Запрос с ID {request_id} не найден!")

    return {"status": "ok"}

logs_folder_path = settings.LOG_FOLDER
logs_manager = LogManager(logs_folder_path, 'bot_logs.csv')

# === Кнопки ===
HELP_BUTTON = 'Помощь'
FILES_LIST_BUTTON = 'Загруженные файлы'
DELETE_FILES_BUTTON = 'Удалить все загруженные файлы'


# === Команды ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    first_name = message.from_user.first_name
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        telebot.types.KeyboardButton(text=HELP_BUTTON),
        telebot.types.KeyboardButton(text=FILES_LIST_BUTTON),
        telebot.types.KeyboardButton(text=DELETE_FILES_BUTTON),
    )
    bot.send_message(message.chat.id,
                     f"""Привет, {first_name}! Я бот помощник. Я помогу тебе найти нужный ответ.
Отправь мне файлы в формате PDF или DOCX и задавай по ним вопросы.
Если хочешь пообщаться не по текстам, то отправь мне сообщение которое начинается с [$]
Если у тебя будут предложения обращайся в Клуб Разработчиков 1С ПРО Консалтинг""",
                     reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def help_bot(message):
    bot.send_message(message.chat.id,
                     f'Вот что я умею:\n'
                     f'1️⃣  {FILES_LIST_BUTTON} - позволяет получить перечень загруженных файлов\n'
                     f'2️⃣  {DELETE_FILES_BUTTON} - выполняет полное удаление всех загруженных ранее файлов')


# === Обработка текстовых сообщений ===
@bot.message_handler(content_types=['text'])
def handle_buttons(message):
    try:

        print("Chat ID:", message.chat.id)
        if is_user_in_chat(message.from_user.id) == False:
             bot.send_message(message.chat.id, 'Извините, это закрытый канал !')
             return

        if message.chat.type != 'private':
            me = bot.get_me()
            username = me.username
            if not message_to_the_bot(username, message.text):
                return
            else:
                username = settings.TELEGRAM_USER    
        elif settings.TELEGRAM_JUST_QUESTIONS:
            username = settings.TELEGRAM_USER
        else:
            username = message.from_user.username

        text = message.text.strip()
        chatID = message.chat.id

        if text == FILES_LIST_BUTTON:
            simpleRequest = request.prepare_request(username, text)
            request_data = {
                "chat_id": chatID,
                "query_text": text,
                "request_uid": simpleRequest.code_uid.request_uid,
                "status": "processing",
                "timestamp": datetime.datetime.now(),
                "response": None,
                "files": [],
                "message_id": message.message_id,
                "username": username
            }
            request_chat_map[simpleRequest.code_uid.request_uid] = request_data
            executor.submit(request.send_request, simpleRequest, '/api/v1/files/list')

        elif text == HELP_BUTTON:
            bot.send_message(message.chat.id,
                             f'Вот что я умею:\n'
                             f'1️⃣  {FILES_LIST_BUTTON} - позволяет получить перечень загруженных файлов\n'
                             f'2️⃣  {DELETE_FILES_BUTTON} - выполняет полное удаление всех загруженных ранее файлов')

        elif text == DELETE_FILES_BUTTON:
            if settings.TELEGRAM_JUST_QUESTIONS:
                bot.send_message(chatID, 'Извините, включен ограниченный режим, нельзя удалять файлы!')
            else:
                simpleRequest = request.prepare_request(username, text)
                request_data = {
                    "chat_id": chatID,
                    "query_text": text,
                    "request_uid": simpleRequest.code_uid.request_uid,
                    "status": "processing",
                    "timestamp": datetime.datetime.now(),
                    "response": None,
                    "files": [],
                    "message_id": message.message_id,
                    "username": username
                }
                request_chat_map[simpleRequest.code_uid.request_uid] = request_data
                executor.submit(request.send_request, simpleRequest, '/api/v1/files/delete')

        elif not text.strip():
            bot.send_message(chatID, 'Извините, необходимо указать запрос!')

        elif text.count('$') == 1:
            bot.send_message(chatID, 'Запрос не по текстам. Секунду, думаю...')
            simpleRequest = request.prepare_request(username, text)
            request_data = {
                "chat_id": chatID,
                "query_text": text,
                "request_uid": simpleRequest.code_uid.request_uid,
                "status": "processing",
                "timestamp": datetime.datetime.now(),
                "response": None,
                "files": [],
                "message_id": message.message_id,
                "username": username
            }
            request_chat_map[simpleRequest.code_uid.request_uid] = request_data
            executor.submit(request.send_request, simpleRequest, '/api/v1/llm/free_answer')

        else:
            bot.send_message(chatID, 'Секунду, думаю...')
            simpleRequest = request.prepare_request(username, text)
            request_data = {
                "chat_id": chatID,
                "query_text": text,
                "request_uid": simpleRequest.code_uid.request_uid,
                "status": "processing",
                "timestamp": datetime.datetime.now(),
                "response": None,
                "files": [],
                "message_id": message.message_id,
                "username": username
            }
            request_chat_map[simpleRequest.code_uid.request_uid] = request_data
            executor.submit(request.send_request, simpleRequest, '/api/v1/llm/answer')

    except Exception as e:
        print(f"[ERROR] handle_buttons: {e}")


# === Обработка документов ===
@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        if message.chat.type != 'private':
            me = bot.get_me()
            username = me.username
            if not message_to_the_bot(username, message.text):
                return
            else:
                username = settings.TELEGRAM_USER 
        elif settings.TELEGRAM_JUST_QUESTIONS:
            username = settings.TELEGRAM_USER
        else:
            username = message.from_user.username

        chatID = message.chat.id
        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name

        if file_name == "prime.xlsx":
            pass  # todo реализовать позже
        elif settings.TELEGRAM_JUST_QUESTIONS:
            bot.send_message(chatID, "Извините, включен ограниченный режим, нельзя добавлять файлы!")
        else:
            downloaded_file = bot.download_file(file_info.file_path)
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
                file_path = temp_file.name
                temp_file.write(downloaded_file)
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type is None:
                    mime_type = 'application/octet-stream'

                with open(file_path, 'rb') as file:
                    files = [('files', (file_name, file.read(), mime_type))]

            request_form = request.prepare_request(username, "")
            request_data = {
                "chat_id": chatID,
                "query_text": "",
                "request_uid": request_form.code_uid.request_uid,
                "status": "processing",
                "timestamp": datetime.datetime.now(),
                "response": None,
                "files": [file_name],
                "message_id": message.message_id,
                "username": username
            }
            request_chat_map[request_form.code_uid.request_uid] = request_data
            response = request.send_file_request(files, request_form, '/api/v1/files/upload')
            if response.status_code != 200:
                bot.send_message(message.chat.id, f"Ошибка при загрузке файла '{file_name}': {response.text}")

            os.remove(file_path)

    except Exception as e:
        print(f"[ERROR] handle_document: {e}")


# === Вспомогательные функции ===
def message_to_the_bot(bot_username, text):
    text = text.strip().lower()
    bot_username = bot_username.strip().lower()
    return f"@{bot_username}" in text

def is_user_in_chat(user_id):
    if not chat_id or chat_id in [0, "0", "", " "]:
        return True
    
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка при проверке участника: {e}")
        return False

# === Запуск бота с перезапуском ===
def start_bot():
    while True:
        try:
            print("БОТ ЗАПУЩЕН!")
            bot.polling(none_stop=True, interval=1)
        except Exception as e:
            print(f"[ERROR] Бот упал: {e}")
            bot.stop_polling()
            print("Перезапуск бота через 5 секунд...")
            time.sleep(5)
        finally:
            bot.stop_polling()
            print("БОТ ОСТАНОВЛЕН")


def start_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8090)


if __name__ == "__main__":
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    start_fastapi()