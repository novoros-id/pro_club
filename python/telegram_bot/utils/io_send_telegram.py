import config
import telebot
from config import settings

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

def send_telegram_message(id, message):
    bot.send_message(id, message)