import config
import telebot
import io_file_operation
# import os

bot = telebot.TeleBot(config.bot_token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    username = message.from_user.username or 'Unknown'
    first_name = message.from_user.first_name or 'User'
    io_file_operation.create_user(chat_id, username)

    # Создаем клавиатуру
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
    username = message.from_user.username or 'Unknown'
    io_file_operation.process_files(chatID, username)

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