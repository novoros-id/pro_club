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

# === Инициализация ===
app = FastAPI()
bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

# Словарь для хранения пар requestId и chatId
request_chat_map = {}

# Объект для выполнения фоновых задач
executor = ThreadPoolExecutor(max_workers=3)

@app.post("/process")
def process_request(data: SimpleResponse):
    request_id = data.code_uid.request_uid
    chat_id = request_chat_map.get(request_id)
    if chat_id:
        try:
            bot.send_message(chat_id=chat_id, text=data.answer)
        except Exception as e:
            print(f"[ERROR] При отправке сообщения: {e}")
    return {"status": "ok"}


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
            request_chat_map[simpleRequest.code_uid.request_uid] = chatID
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
                request_chat_map[simpleRequest.code_uid.request_uid] = chatID
                executor.submit(request.send_request, simpleRequest, '/api/v1/files/delete')

        elif not text.strip():
            bot.send_message(chatID, 'Извините, необходимо указать запрос!')

        elif text.count('$') == 1:
            bot.send_message(chatID, 'Запрос не по текстам. Секунду, думаю...')
            simpleRequest = request.prepare_request(username, text)
            request_chat_map[simpleRequest.code_uid.request_uid] = chatID
            executor.submit(request.send_request, simpleRequest, '/api/v1/llm/free_answer')

        else:
            bot.send_message(chatID,
                             'Секунду, думаю...')
            simpleRequest = request.prepare_request(username, text)
            request_chat_map[simpleRequest.code_uid.request_uid] = chatID
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
            request_chat_map[request_form.code_uid.request_uid] = chatID
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