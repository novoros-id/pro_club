from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks, Request
import json
from app.services.file_service import FileService
from app.models import SimpleRequest
from app.deps import CurrentUser, DB_Provider, get_user, get_db_provider
from app.core.provider_db import Provider


file_service = FileService()

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/")
async def read_root():
    return {"message": "root files"} 

@router.post("/upload")
async def upload_files(
    request: Request,
    background_tasks: BackgroundTasks,
    db_provider: Provider = Depends(get_db_provider),
    request_form: str = Form(...), 
    files: list[UploadFile] = File(...)
    ):
    # Из-за ограничения, что нельзя передавать в Body json и файлы, модель передается как Form 
    request_data = json.loads(request_form)
    request = SimpleRequest(**request_data)
    
    user = get_user(request, db_provider)
        
    # Сохраняет файлы в папку Input и запускает их на обработку
    await file_service.save_files_and_process(user, files, request, db_provider, background_tasks)
    return status.HTTP_200_OK

@router.post("/process")
async def process_user_files(request: SimpleRequest, 
                             user: CurrentUser,
                             db_provider: DB_Provider,
                             background_tasks: BackgroundTasks):
    background_tasks.add_task(file_service.process_user_files, request, user, db_provider)
    return status.HTTP_200_OK

@router.post("/list")
async def get_list_files(request: SimpleRequest, 
                         user: CurrentUser,
                         db_provider: DB_Provider,
                         background_tasks: BackgroundTasks):
    background_tasks.add_task(file_service.get_list_files, request, user, db_provider)
    return status.HTTP_200_OK

@router.post("/delete")
async def delete_all_user_files(request: SimpleRequest, 
                                user: CurrentUser,
                                db_provider: DB_Provider,
                                background_tasks: BackgroundTasks):
    await file_service.delete_all_user_files(request, user, db_provider, background_tasks)
    return status.HTTP_200_OK
