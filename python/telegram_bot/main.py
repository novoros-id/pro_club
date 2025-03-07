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
    """  try:
        print (data)
        # Проверяем, есть ли в JSON нужные ключи
        if "code_uid" in data and "request" in data:
            code_uid = data["code_uid"]
            if all(k in code_uid for k in ["username", "program_uid", "request_uid"]):
                await asyncio.sleep(2)  # Ожидание 2 секунды
                return {
                    "code_uid": code_uid,
                    "answer": "ОК"
                }
        
        # Если данные не соответствуют ожидаемой структуре
        await asyncio.sleep(2)
        return {"error": "Некорректный JSON", "received_data": data}
    
    except Exception as e:
        await asyncio.sleep(2)
        print (e)
        return {"error": "Ошибка обработки", "details": str(e)}
 """

