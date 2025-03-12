
import httpx
import uuid
import json
import mimetypes
from models import SimpleRequest
from config import settings

async def send_request(response_data: SimpleRequest, endpoint: str) -> httpx.Request:

    url = settings.API_URL + endpoint

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        request = await client.post(url, headers=headers, json=response_data.dict())
        return request
    
async def send_file_request(files: list[str], request: SimpleRequest, endpoint: str) -> httpx.Response:
    
    url = settings.API_URL + endpoint
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

    headers = {
        "accept": "application/json",
        "Content-Type": f"multipart/form-data; boundary={boundary}"
       }
    
    data = {'request_form': json.dumps(request.dict())}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files, data=data)
        return response
    
def prepare_request(user_name: str, text: str) -> SimpleRequest:

    return SimpleRequest(
        code_uid={
            "username": user_name,
            "program_uid": settings.PROGRAM_UID,
            "request_uid": generate_request_uid()
        },
        request=text
    )

def generate_request_uid():
    return str(uuid.uuid4())

def get_curl_command(file_paths: list[str], data: str, endpoint: str) -> str:
    url = settings.API_URL + endpoint
 
    curl_command = f"curl -X POST '{url}' -H 'accept: application/json' -H 'Content-Type: multipart/form-data'"

    for file_path in file_paths:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        curl_command += f" -F 'files=@{file_path};type={mime_type}'"

    curl_command += f" -F 'request_form={data}'"

    return curl_command