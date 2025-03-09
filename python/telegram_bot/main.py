from fastapi import FastAPI
import asyncio
from typing import Any
from pydantic import BaseModel
import telebot
from config import settings


class SimpleRequest(BaseModel):
    username: str
    program_uid: str
    request_uid: str
    answer: str | None = None

app = FastAPI()

""" bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
chatID = settings.TELEGRAM_CHAT_ID """


@app.post("/process")
async def process_request(data: SimpleRequest):
    import requests
    response = requests.post(
        f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": settings.TELEGRAM_CHAT_ID, "text": data.answer}
    )
    #bot.send_message(chatID, data.answer)
    #return {"error": "Некорректный JSON", "received_data": data}


