import config_vgn
import telebot
import time

bot = telebot.TeleBot(config_vgn.token)

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет! Я бот для теста (vgn).')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
  time.sleep(int(message.text))
  bot.send_message(message.chat.id, 'Привет! Я бот для теста (vgn).' + message.text)
bot.polling()