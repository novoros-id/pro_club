import httpx
from typing import Dict, Any
from app.models import SimpleRequest, SimpleResponse
from app.config import settings

async def send_request(response_data: SimpleResponse, request_name: str) -> httpx.Response:

    url = get_url_root(response_data.code_uid.program_uid)
    endpoint = get_endpoint("process")
    url += endpoint

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=response_data.dict())
        return response

def get_url_root(program_uid: str) -> str:

    match program_uid.upper(): 
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