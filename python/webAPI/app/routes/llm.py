from fastapi import APIRouter, Depends, HTTPException
from app.models import SimpleRequest, UserBase
from app.services.llm_service import LLMService
from app.utils.response import send_request, create_simple_response_from_request

from app.deps import CurrentUser

llm_service = LLMService()

router = APIRouter(prefix="/llm", tags=["llm"])

@router.get("/")
async def read_root():
    return {"message": "root llm"} 

@router.post("/answer")
async def get_answer(request: SimpleRequest, user: CurrentUser):
    answer = await llm_service.get_answer_service(request, user)
    simple_response = create_simple_response_from_request(request, answer)
    response = await send_request(simple_response, "get_answer_service")


@router.post("/free_answer")
async def get_free_answer(request: SimpleRequest, user: CurrentUser):
    answer = await llm_service.get_free_answer_service(request, user)
    simple_response = create_simple_response_from_request(request, answer)
    response = await send_request(simple_response, "get_free_answer_service")
