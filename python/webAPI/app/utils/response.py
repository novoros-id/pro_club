import httpx
from fastapi import Depends
from typing import Dict, Any
from app.models import SimpleRequest, SimpleResponse
from app.db_models import TypeProgram
from app.config import settings
import base64
from app.deps import get_db_provider, DB_Provider
from app.core.provider_db import Provider, DataProvider

# Путь к файлу с JSON (замени на свой)
#JSON_FILE_PATH = "app/utils/clients.json"

""" # Глобальные переменные для кэша
_database_cache = None
_cache_lock = threading.Lock() """


async def send_request(response_data: SimpleResponse, request_name: str, db_provider: Provider) -> httpx.Response:

    program_connection = db_provider.get_connection_settings(response_data.code_uid.program_uid)
    url = program_connection.url + "/" + program_connection.endpoint
    
    if program_connection.clienttype == TypeProgram.Telegram.value:

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=response_data.dict())
            response.raise_for_status() 
            return response
    else:

        username = program_connection.client_login
        password = program_connection.client_pass
        credentials = f"{username}:{password}".encode("utf-8")
        encoded_credentials = base64.b64encode(credentials).decode("utf-8")

        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=response_data.dict())
            response.raise_for_status() 
            return response

""" def load_database_config():
    #Загружает JSON в память, если он еще не загружен
    global _database_cache
    if _database_cache is None:  # Ленивая загрузка
        with _cache_lock:
            if _database_cache is None:  # Повторная проверка (чтобы исключить race condition)
                try:
                    with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
                        _database_cache = json.load(file)
                except () as e:
                    print(f"Ошибка при загрузке JSON: {e}")
                    _database_cache = {}

def get_database_config(program_uid):
    #Возвращает конфигурацию базы, лениво загружая JSON при первом вызове.
    load_database_config()  # Проверяем, загружен ли кэш
    return _database_cache.get(program_uid, None)

def reload_database_config():
    #Принудительно обновляет кэш (если JSON изменился).
    global _database_cache
    with _cache_lock:
        _database_cache = None  # Сбрасываем кэш
    load_database_config()  # Перезагружаем данн """

##############################
##############################
##############################

async def send_request_(response_data: SimpleResponse, request_name: str) -> httpx.Response:

    url = get_url_root(response_data.code_uid.program_uid)
    endpoint = get_endpoint("process")
    url += endpoint


    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=response_data.dict())
        response.raise_for_status() 
        return response

def get_url_root(program_uid: str) -> str:

    match program_uid: 
        case settings.UID_PROGRAM_1C:
            return settings.URL_1C_ROOT
        case settings.UID_PROGRAM_TELEBOT:
            return settings.URL_TELEBOT_ROOT
        case _:
            return ""

def get_endpoint(request_name: str) -> str:
    endpoint = "/{request_name}"
    return endpoint.format(request_name=request_name)

def create_simple_response_from_request(simple_request: SimpleRequest, answer: str) -> dict[str, Any]:
    response_data = simple_request.model_dump()
    response_data["answer"] = answer
    return SimpleResponse(**response_data)
