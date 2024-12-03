import config_vgn
import telebot

bot = telebot.TeleBot(config_vgn.token)

def send_(id, tt):
    bot.send_message(id, tt)