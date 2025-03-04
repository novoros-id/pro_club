from fastapi import APIRouter, Depends, HTTPException
from app.models import Question, QuestionPublic
from app.services.llm_service import LLMService

llm_service = LLMService()

router = APIRouter(prefix="/llm", tags=["llm"])

@router.get("/")
async def read_root():
    return {"message": "root llm"} 

@router.post("/get_answer")
async def get_answer(question: Question):
    return await llm_service.get_answer_service(question)

@router.post("/get_free_answer")
async def get_free_answer(question: Question):
    return await llm_service.get_free_answer_service(question)