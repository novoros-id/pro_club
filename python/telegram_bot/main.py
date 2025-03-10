from fastapi import FastAPI
import asyncio
from typing import Any
from pydantic import BaseModel
import telebot
from config import settings

class CodeUID(BaseModel):
    username: str
    program_uid: str
    request_uid: str

class SimpleRequest(BaseModel):
    answer : str | None = None

app = FastAPI()
bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


@app.post("/process")
async def process_request(data: SimpleRequest):
    import requests

    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=data.answer)

    """ response = requests.post(
         f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": settings.TELEGRAM_CHAT_ID, "text": data.answer} 
    ) """


