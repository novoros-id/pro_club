from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
import json
from typing import Annotated
from app.services.file_service import return_user_folder_input, get_list_user_files, delete_all_files, process_files
from app.utils.io_db import DbHelper
#from app.services.user_service import UserService
from app.models import SimpleRequest
from app.utils.response import send_request, create_simple_response_from_request
from app.deps import CurrentUser, get_user

""" file_service = FileService()
user_service = UserService(file_service) """
#user_service = UserService()

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/")
async def read_root():
    return {"message": "root files"} 

@router.post("/upload")
async def upload_files(
    request_form: str = Form(...), 
    files: list[UploadFile] = File(...)):
    # Из-за ограничения, что нельзя передавать в Body json и файлы, модель передается как Form 
    request_data = json.loads(request_form)
    request = SimpleRequest(**request_data)
    user = get_user(request)

    # Сохраняет файлы в папку Input
    files_list = []
    for file in files:
        filename = file.filename
        file_path = return_user_folder_input(user)
        with open(f"{file_path}/{filename}", "wb") as buffer:
            buffer.write(file.file.read())
            files_list.append(filename)
    files_str = ', '.join(files_list)
    response_text = f"Файл(ы) '{files_str}' успешно загружен(ы)! Начинаю обработку файла.\nВ зависимости от размера файла время обработки может увеличиваться."
    simple_response = create_simple_response_from_request(request, response_text)
    response = await send_request(simple_response, "upload")

    # Обработает загруженные файлы
    process_files(request, user)


@router.post("/process")
async def process_user_files(request: SimpleRequest, user: CurrentUser):
    result_processin_files = process_files(user)
    db_helper = DbHelper(user)
    db_helper.processing_user_files()
    response_text = f"Файл(ы) '{result_processin_files["files"]}' успешно обработан(ы)."
    simple_response = create_simple_response_from_request(request, response_text)
    response = await send_request(simple_response, "upload")

@router.post("/list")
async def get_list_files(request: SimpleRequest, user: CurrentUser):
    list_files = get_list_user_files(user)
    simple_response = create_simple_response_from_request(request, list_files)
    response = await send_request(simple_response, "list_files")

@router.post("/delete")
async def delete_all_user_files(request: SimpleRequest, user: CurrentUser):
    #читка файловой системы
    delete_all_files(user)
    #удаление структуры LLM
    db_helper = DbHelper(user)
    db_helper.delete_all_user_db()
    simple_response = create_simple_response_from_request(request, "Файлы удалены")
    response = await send_request(simple_response, "delete_files")
