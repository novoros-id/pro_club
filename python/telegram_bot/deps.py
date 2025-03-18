import telebot
from fastapi import Depends
from typing import Annotated
from config import settings

def get_bot() -> telebot.TeleBot:
    return telebot.TeleBot(settings.TELEGRAM_TOKEN)

CurrenBot = Annotated[telebot.TeleBot, Depends(get_bot)]