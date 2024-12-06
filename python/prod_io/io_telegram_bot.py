import config
import telebot
import os

bot = telebot.TeleBot(config.bot_token)

#Тестовая папка для сохранения файлов
test_download_folder = "test_download"
if not os.path.exists(test_download_folder):
    os.makedirs(test_download_folder)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    username = message.from_user.username or 'Unknown'
    first_name = message.from_user.first_name or 'User'
    # Создаем клаву
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    help_button = telebot.types.KeyboardButton(text="Помощь")
    keyboard.add(help_button)
    bot.send_message(message.chat.id, # Отправка приветствия
        f"Привет, {first_name}! Я MindCatcher бот. Я помогу тебе найти нужный ответ \n\n"
        , reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
def help_bot(message):
    bot.send_message(message.chat.id, 
    "Вот что я умею:\n\n"
        "1️⃣  Используй '/start' для возврата в Главное меню\n"
        #"2️⃣  Используй '/ask_bot' - задать вопрос, получить ответ по базе данных (функция в разработке)\n"
        #"3️⃣  Используй '/training' - меню обучения бота (функция в разработке)\n"
    )

# ---= ОБРАБОТКА ТЕКСТОВЫХ КОМАНД =---
@bot.message_handler(content_types=['text'])
def handle_buttons(message):
    text = message.text
    chatID = message.chat.id
    if text == "Помощь":    
        help_bot(message)
    else:
        bot.send_message(chatID, f"Вы отправили сообщение: '{text}'")
        bot.send_message(chatID, "Функции обработки запроса пока нет. Вызывай /help, там описание всех моих функций")

# ---= ОБРАБОТКА ДОКУМЕТОВ =---
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chatID = message.chat.id
    document_ID = message.document.file_id
    document_name = message.document.file_name

    try:
        # Загружаем файл
        file_info = bot.get_file(document_ID)
        download_file = bot.download_file(file_info.file_path)

        # Сохраняем файл
        file_path = os.path.join(test_download_folder, document_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(download_file)

        # УВЕДОМЛЯЕМ ПОЛЬЗОВАТЕЛЯ
        bot.send_message(chatID, f"Файл '{document_name}' успешкно скачан")
    except Exception as e:
        bot.send_message(chatID, f"Произошла ошибка при скачивании файла: {e}")

# ---= ОБРАБОТКА НЕПОДДЕРЖИВАЕМЫХ ДОКУМЕТОВ =---
@bot.message_handler(content_types=['photo', 'audio', 'video', 'voice', 'sticker', 'animation', 'video_note'])
def handle_unsupported_files(message):
    bot.send_message(message.chat.id, "Извините, я обрабатываю только документы. Пожалуйста, отправьте корректный формат файла")

# ---= ЗАПУСК БОТА =---
try:
    print("БОТ ЗАПУЩЕН!")
    bot.polling(none_stop=True, interval=1)
except Exception as e:
    # Информация об ошибке 
    print(f"Ошибка:{e}")
finally:
    # Корретная остановка бота
    bot.stop_polling()
    print("БОТ ОСТАНОВЛЕН")