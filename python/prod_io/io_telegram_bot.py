import config_ds
import io_file_operation
import telebot

bot = telebot.TeleBot(config_ds.bot_token)

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет! Я бот для теста (vgn).')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
  io_file_operation.create_user (bot, message.chat.id, message.from_user.username)
bot.polling()