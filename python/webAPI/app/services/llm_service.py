from fastapi import HTTPException, status
from typing import Any
from app.models import UserBase, SimpleRequest
from app.utils.io_db import DbHelper

class LLMService:
    async def get_answer_service(self, request: SimpleRequest, user: UserBase) -> Any:
        db_helper = DbHelper(user)
        answer = db_helper.get_answer(prompt=request.request)
        return answer

    async def get_free_answer_service(self, request: SimpleRequest, user: UserBase) -> Any:
        db_helper = DbHelper(user)
        answer = db_helper.get_free_answer(prompt=request.request)
        return answer