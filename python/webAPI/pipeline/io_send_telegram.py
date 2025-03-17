import config
import telebot

bot = telebot.TeleBot(config.bot_token)

def send_telegram_message(id, message):
    bot.send_message(id, message)