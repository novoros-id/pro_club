import config_vgn
import io_universal
import telebot

bot = telebot.TeleBot(config_vgn.token)

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет! Я бот для теста (vgn).')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
  print(message.from_user.username)
  file_name = io_universal.sanitize_filename(message.from_user.username)
  bot.reply_to(message, 'Эхо сообщения: ' + message.text + ' . file name ' + file_name)

bot.polling()