from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.models import SimpleRequest, UserBase
from app.services.llm_service import LLMService
import app.utils.response as response_utils

from app.deps import CurrentUser

llm_service = LLMService()

router = APIRouter(prefix="/llm", tags=["llm"])

@router.get("/")
async def read_root():
    return {"message": "root llm"} 

@router.post("/answer")
async def get_answer(request: SimpleRequest, user: CurrentUser, background_tasks: BackgroundTasks):
    background_tasks.add_task(llm_service.get_answer_service, request, user)
    return status.HTTP_200_OK

@router.post("/free_answer")
async def get_free_answer(request: SimpleRequest, user: CurrentUser, background_tasks: BackgroundTasks):
    background_tasks.add_task(llm_service.get_free_answer_service, request, user)
    return status.HTTP_200_OK
