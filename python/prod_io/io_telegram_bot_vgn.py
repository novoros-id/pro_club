import config
import io_file_operation
import telebot
import os

bot = telebot.TeleBot(config.bot_token)

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет! Я бот для теста (vgn).')
    io_file_operation.create_user (message.chat.id, message.from_user.username)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
  io_file_operation.create_user (message.chat.id, message.from_user.username)
  io_file_operation.get_list_files(message.chat.id, message.from_user.username)
  io_file_operation.delete_all_files(message.chat.id, message.from_user.username)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chatID = message.chat.id
    document_ID = message.document.file_id
    document_name = message.document.file_name
    io_file_operation.create_user (message.chat.id, message.from_user.username)

    try:
        # Загружаем файл
        file_info = bot.get_file(document_ID)
        download_file = bot.download_file(file_info.file_path)
        user_folder = io_file_operation.return_user_folder_input(message.from_user.username)

        # Сохраняем файл
        file_path = os.path.join(user_folder, document_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(download_file)

        # УВЕДОМЛЯЕМ ПОЛЬЗОВАТЕЛЯ
        #bot.send_message(chatID, f"Файл '{document_name}' успешно скачан")
        io_file_operation.process_files(message.chat.id, message.from_user.username)
    except Exception as e:
        bot.send_message(chatID, f"Произошла ошибка при скачивании файла: {e}")


bot.polling()