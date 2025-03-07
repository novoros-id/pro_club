from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
import json
from typing import Annotated
from app.services.file_service import return_user_folder_input, get_list_user_files, delete_all_files
from app.utils.io_db import DbHelper
#from app.services.user_service import UserService
from app.models import SimpleRequest
from app.utils.response import send_request, create_simple_response_from_request

""" file_service = FileService()
user_service = UserService(file_service) """

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/")
async def read_root():
    return {"message": "root files"} 

@router.post("/upload")
async def download_files(request_form: str = Form(...), files: list[UploadFile] = File(...)):
    # Из-за ограничения, что нельзя передавать в Body json и файлы, модель передается как Form 
    request_data = json.loads(request_form)
    request = SimpleRequest(**request_data)
    for file in files:
        filename = file.filename
        file_path = return_user_folder_input(request.username)
        with open(f"{file_path}/{filename}", "wb") as buffer:
            buffer.write(file.file.read())
    simple_response = create_simple_response_from_request(request, "Файлы загружены")
    response = await send_request(simple_response, "upload_files")

@router.post("/list")
async def get_list_files(request: SimpleRequest):
    list_files = get_list_user_files(request.username)
    simple_response = create_simple_response_from_request(request, list_files)
    response = await send_request(simple_response, "list_files")

@router.post("/delete")
async def delete_all_user_files(request: SimpleRequest):
    #читка файловой системы
    delete_all_files(request.username)
    #удаление структуры LLM
    db_helper = DbHelper(request.username)
    db_helper.delete_all_user_db()
    simple_response = create_simple_response_from_request(request, "Файлы удалены")
    response = await send_request(simple_response, "delete_files")
