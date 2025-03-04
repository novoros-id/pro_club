from fastapi import HTTPException, status
from typing import Any
from app.models import Question, QuestionPublic

class LLMService:
    async def get_answer_service(self, question: Question) -> Any:
        if question.user_id == "1":
            return QuestionPublic(user_id=question.user_id, answer="bla bla bla")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    async def get_free_answer_service(self, question: Question) -> Any:
        return {"answer": "test get_free_answer"}