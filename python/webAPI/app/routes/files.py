from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
import json
from app.services.file_service import FileService
from app.models import SimpleRequest
from app.deps import CurrentUser, get_user

file_service = FileService()

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/")
async def read_root():
    return {"message": "root files"} 

@router.post("/upload")
async def upload_files(
    background_tasks: BackgroundTasks,
    request_form: str = Form(...), 
    files: list[UploadFile] = File(...)
    ):
    # Из-за ограничения, что нельзя передавать в Body json и файлы, модель передается как Form 
    request_data = json.loads(request_form)
    request = SimpleRequest(**request_data)
    user = get_user(request)

    # Сохраняет файлы в папку Input и запускает их на обработку
    await file_service.save_files_and_process(user, files, request, background_tasks)
    return status.HTTP_200_OK

@router.post("/process")
async def process_user_files(request: SimpleRequest, 
                             user: CurrentUser,
                             background_tasks: BackgroundTasks):
    background_tasks.add_task(file_service.process_user_files, user, request)
    return status.HTTP_200_OK

@router.post("/list")
async def get_list_files(request: SimpleRequest, 
                         user: CurrentUser, 
                         background_tasks: BackgroundTasks):
    background_tasks.add_task(file_service.get_list_files, request, user)
    return status.HTTP_200_OK

@router.post("/delete")
async def delete_all_user_files(request: SimpleRequest, 
                                user: CurrentUser,
                                background_tasks: BackgroundTasks):
    await file_service.delete_all_user_files(request, user, background_tasks)
    return status.HTTP_200_OK
