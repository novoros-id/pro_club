import config
import telebot

bot = telebot.TeleBot(config.bot_token)

def send_telegram_message(id, tt):
    bot.send_message(id, tt)