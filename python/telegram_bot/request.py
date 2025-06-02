import requests
import uuid
import json
import mimetypes
from models import SimpleRequest
from config import settings


def send_request(response_data: SimpleRequest, endpoint: str) -> requests.Response:
    """
    Отправляет JSON-запрос к API
    """
    url = settings.API_URL + endpoint

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=response_data.dict())
    return response


def send_file_request(files: list, request: SimpleRequest, endpoint: str) -> requests.Response:
    """
    Отправляет файлы и данные формы на указанный эндпоинт
    """
    url = settings.API_URL + endpoint

    # Генерируем boundary вручную или используем автоматически создаваемый requests
    data = {'request_form': json.dumps(request.dict())}

    # multipart/form-data запрос будет создан автоматически
    response = requests.post(url, files=files, data=data)
    return response


def prepare_request(user_name: str, text: str) -> SimpleRequest:
    """
    Подготавливает объект запроса
    """
    return SimpleRequest(
        code_uid={
            "username": user_name,
            "program_uid": settings.PROGRAM_UID,
            "request_uid": generate_request_uid()
        },
        request=text
    )


def generate_request_uid():
    """
    Генерирует уникальный ID запроса
    """
    return str(uuid.uuid4())


def get_curl_command(file_paths: list[str], data: str, endpoint: str) -> str:
    """
    Генерирует команду curl для отладки
    """
    url = settings.API_URL + endpoint

    curl_command = f"curl -X POST '{url}' -H 'accept: application/json' -H 'Content-Type: multipart/form-data'"

    for file_path in file_paths:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        curl_command += f" -F 'files=@{file_path};type={mime_type}'"

    curl_command += f" -F 'request_form={data}'"

    return curl_command