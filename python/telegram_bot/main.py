import telebot
import threading
import uvicorn
from fastapi import FastAPI
from config import settings
import request
from models import SimpleResponse
import asyncio
import tempfile
import os
import mimetypes

# Словарь для хранения пар requestId и chatId
request_chat_map = {}

app = FastAPI()
@app.post("/process")
async def process_request(data: SimpleResponse):
    request_id = data.code_uid.request_uid
    chat_id = request_chat_map.get(request_id)

    if chat_id:
        bot.send_message(chat_id=chat_id, text=data.answer)
        # Удаляем пару после обработки
        #пока убрал так как в рамках загрузки файлов используется один идентификатор загрузки и орбработки.
        #del request_chat_map[request_id]


HELP_BUTTON = 'Помощь'
FILES_LIST_BUTTON = 'Загруженные файлы'
DELETE_FILES_BUTTON = 'Удалить все загруженные файлы'

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

# ---= ОБРАБОТКА КОМАНД =---
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
        f"""Привет, {first_name}! Я бот помощник. Я помогу тебе найти нужный ответ
        Отправь мне файлы в формате PDF или DOCX и задавай по ним вопросы
        Если хочешь пообщаться не по текстам, то отправь мне сообщение которое начинается с [$]
        Если у тебя будут предложения обращайся в Клуб Разработчиков 1С ПРО Консалтинг \n\n"""
        , reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
def help_bot(message):
    bot.send_message(message.chat.id, 
        f'Вот что я умею:\n\n'
        f'1️⃣  {FILES_LIST_BUTTON} - позволяет получить перечень загруженных файлов\n'
        f'2️⃣  {DELETE_FILES_BUTTON} - выполняет полное удаление всех загруженных ранее файлов'
    )

# ---= ОБРАБОТКА ТЕКСТОВЫХ КОМАНД =---
@bot.message_handler(content_types=['text'])
def handle_buttons(message):
    asyncio.run(handle_buttons_async(message))

async def handle_buttons_async(message):

    if  message.chat.type != 'private':
        me = bot.get_me()
        username = me.username #message.chat.title
        if message_to_the_bot(username, message.text) == False:
            return
    elif settings.TELEGRAM_JUST_QUESTIONS == True:
        username = settings.TELEGRAM_USER
    else: 
        username = message.from_user.username

    text = message.text.strip()
    chatID = message.chat.id
   
    #request_time = datetime.datetime.now()
    #input_user_files = io_file_operation.return_user_folder_input(username)

    if text == FILES_LIST_BUTTON:
        simpleRequest = request.prepare_request(username, text)
        request_chat_map[simpleRequest.code_uid.request_uid] = chatID
        await request.send_request(simpleRequest, '/api/v1/files/list')
    elif text == HELP_BUTTON:
        bot.send_message(message.chat.id, 
            f'Вот что я умею:\n\n'
            f'1️⃣  {FILES_LIST_BUTTON} - позволяет получить перечень загруженных файлов\n'
            f'2️⃣  {DELETE_FILES_BUTTON} - выполняет полное удаление всех загруженных ранее файлов'
        )
    elif text == DELETE_FILES_BUTTON:
        if settings.TELEGRAM_JUST_QUESTIONS == False:
            simpleRequest = request.prepare_request(username, text)
            request_chat_map[simpleRequest.code_uid.request_uid] = chatID
            await request.send_request(simpleRequest, '/api/v1/files/delete')
        else:
            response_text =  'Извините, включен ограниченный режим, нельзя удалять файлы!'
            bot.send_message(chatID, response_text)

    else:
        if not text.strip():
            response_text = (chatID, 'Извините, необходимо указать запрос!')
            bot.send_message(chatID, response_text)

        elif text.startswith ('$'):
            bot.send_message(chatID, 'Запрос не по текстам. Подготовка ответа может занять некоторое время...')
            simpleRequest = request.prepare_request(username, text)
            request_chat_map[simpleRequest.code_uid.request_uid] = chatID
            await request.send_request(simpleRequest, '/api/v1/llm/free_answer')

        else:
            bot.send_message (chatID, 'Запрос к загруженным текстам, это тестовый сервер и для ответа необходимо более одной минуты. Вы можете перейти к другим задачам, а когда я буду готов, то Вам придет оповещение')
            simpleRequest = request.prepare_request(username, text)
            request_chat_map[simpleRequest.code_uid.request_uid] = chatID
            await request.send_request(simpleRequest, '/api/v1/llm/answer')
            """   try:
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
                print(f'Ошибка в get_answer: {e}') """
    
# ---= ОБРАБОТКА ДОКУМЕНТОВ =---
@bot.message_handler(content_types=['document'])
def handle_document(message):
    asyncio.run(handle_document_async(message))

async def handle_document_async(message):
  
    if  message.chat.type != 'private':
        me = bot.get_me()
        username = me.username #message.chat.title
        if message_to_the_bot(username, message.text) == False:
            return
    elif settings.TELEGRAM_JUST_QUESTIONS == True:
        username = settings.TELEGRAM_USER
    else: 
        username = message.from_user.username

    chatID = message.chat.id
    file_info = bot.get_file(message.document.file_id)
    file_name = message.document.file_name

    if file_name == "prime.xlsx":
       # todo сделать позже
       """  print ("Загрузка файла prime.xlsx")
        # Загружаем файл
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем временный файл
        temp_file_path = f"/tmp/{file_name}"
        with open(temp_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Проверка содержимого файла
        if not validate_file_structure(temp_file_path):
            os.remove(temp_file_path) #удаляем временный файл
            bot.send_message(chatID, "Ошибка: Файл должен содержать колонки 'request_text', 'response_text', 'Source'")
            return
        
        # Обновляем файл 
        update_prime_file(temp_file_path, chatID) """
    else:
        if settings.TELEGRAM_JUST_QUESTIONS == False:
            dowloaded_file = bot.download_file(file_info.file_path)
            files = []
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
                temp_file.write(dowloaded_file)
                file_path = temp_file.name
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type is None:
                    mime_type = 'application/octet-stream'  # Default MIME type if unknown
                with open(file_path, 'rb') as file:
                    files.append(('files', (file_name, file.read(), mime_type)))
    
            request_form = request.prepare_request(username, "")
            request_chat_map[request_form.code_uid.request_uid] = chatID
            response = await request.send_file_request(files, request_form, '/api/v1/files/upload')
            if response.status_code == 200:
                pass
            else:
                bot.send_message(message.chat.id, f"Ошибка при загрузке файла '{file_name}': {response.text}")

            os.remove(file_path)
        else:
            response_text = "Извините, включен ограниченный режим, нельзя добавлять файлы!"
            bot.send_message(chatID, response_text)


def start_bot():
    try:
        print("БОТ ЗАПУЩЕН!")
        bot.polling(none_stop=True, interval=1)
    except Exception as e:
    # Информация об ошибке 
        print(f"Ошибка:{e}")
    finally:
        bot.stop_polling()
        print("БОТ ОСТАНОВЛЕН")

def start_fastapi():
    uvicorn.run(app, host="127.0.0.2", port=8000)

def message_to_the_bot(bot_username, text):
    text = text.strip().lower()
    bot_username = bot_username.strip().lower()
    if f"@{bot_username}" in text:
        return True
    else:
        return False

if __name__ == "main":
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

#debug Нужен для ответа в дебаш чат
request_chat_map[settings.DEBUG_REQUEST_ID] = settings.DEBUG_TELEGRAM_CHAT_ID
