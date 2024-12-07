import config
import telebot
import io_file_operation
import io_db
import os

bot = telebot.TeleBot(config.bot_token)

HELP_BUTTON = 'Помощь'
FILES_LIST_BUTTON = 'Загруженные файлы'
DELETE_FILES_BUTTON = 'Удалить все загруженные файлы'

# ---= ОБРАБОТКА КОМАНД =---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    io_file_operation.create_user(chat_id, username)

    # Создаем клавиатуру
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        telebot.types.KeyboardButton(text=HELP_BUTTON),
        telebot.types.KeyboardButton(text=FILES_LIST_BUTTON),
        telebot.types.KeyboardButton(text=DELETE_FILES_BUTTON),
    )

    bot.send_message(message.chat.id,
        f"""Привет, {first_name}! Я бот помощник. Я помогу тебе найти нужный ответ
         Отправь мне файлы в формате PDF и задавай по ним вопросы
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

# ---= ОБРАБОТКА ТЕКСТОВЫХ КОМАНД =---
@bot.message_handler(content_types=['text'])
def handle_buttons(message):
    text = message.text
    chatID = message.chat.id
    username = message.from_user.username
    io_file_operation.create_user(chatID, username)
    if text == HELP_BUTTON:    
        help_bot(message)
    elif text == FILES_LIST_BUTTON:
        io_file_operation.get_list_files(chatID, username)
    elif text == DELETE_FILES_BUTTON:
        io_file_operation.delete_all_files(chatID, username)
    else:
        if text == "":
            bot.send_message(chatID, 'Извините, необходимо указать запрос!')
        elif text[0] == ".":
            bot.send_message(chatID, 'Запрос не по текстам, необходимо немного времени на подготовку ответа')
            db_helper = io_db.DbHelper(chat_id=chatID, user_name=username)
            answer = db_helper.get_free_answer(prompt=text)
            bot.send_message(chatID, answer)
        else:
            bot.send_message(chatID, 'Запрос к загруженным текстам, необходимо немного времени на подготовку ответа')
            try:
                db_helper = io_db.DbHelper(chat_id=chatID, user_name=username)
                answer = db_helper.get_answer(prompt=text)
                if answer:
                    bot.send_message(chatID, f'Ответ: {answer}')
                else:
                    bot.send_message(chatID, 'Извините, я не смог сформировать ответ!')
            except Exception as e:
                bot.send_message(chatID, 'Произошла ошибка при обработке запроса.')
                print(f'Ошибка в get_answer: {e}')

# ---= ОБРАБОТКА ДОКУМЕТОВ =---
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chatID = message.chat.id
    username = message.from_user.username
    io_file_operation.create_user(chatID, username)
    file_info = bot.get_file(message.document.file_id)
    file_name = message.document.file_name

    dowloaded_file = bot.download_file(file_info.file_path)
    user_input_folder = io_file_operation.return_user_folder_input(username)
    save_path = os.path.join(user_input_folder, file_name)
    
    with open(save_path, 'wb') as new_file:
        new_file.write(dowloaded_file)

    io_file_operation.process_files(chatID, username)

    bot.send_message(chatID, f"Файл '{file_name}' успешно загружен и обработан")

# ---= ОБРАБОТКА НЕПОДДЕРЖИВАЕМЫХ ДОКУМЕТОВ =---
@bot.message_handler(content_types=['photo', 'audio', 'video', 'voice', 'sticker', 'animation', 'video_note'])
def handle_unsupported_files(message):
    bot.send_message(message.chat.id, "Извините, я обрабатываю только текстовые документы (например PDF, TXT или DOC). Пожалуйста, отправьте корректный формат файла")

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