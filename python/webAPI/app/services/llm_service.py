from typing import Any
from app.models import UserBase, SimpleRequest
from app.utils.io_db import DbHelper
import app.utils.response as response_utils
from app.core.provider_db import Provider

class LLMService:
    async def get_answer_service(self, 
                                 request: SimpleRequest, 
                                 user: UserBase,
                                 db_provider: Provider) -> Any:
        db_helper = DbHelper(user)
        answer = db_helper.get_answer(prompt=request.request)
        simple_response = response_utils.create_simple_response_from_request(request, answer)
        response = await response_utils.send_request(simple_response, "get_answer_service", db_provider)

    async def get_free_answer_service(self, 
                                      request: SimpleRequest, 
                                      user: UserBase,
                                      db_provider: Provider) -> Any:
        db_helper = DbHelper(user)
        answer = db_helper.get_free_answer(prompt=request.request)
        simple_response = response_utils.create_simple_response_from_request(request, answer)
        response = await response_utils.send_request(simple_response, "get_free_answer_service", db_provider)

    async def get_search_answer_service(self, 
                                      request: SimpleRequest, 
                                      user: UserBase,
                                      db_provider: Provider) -> Any:
        db_helper = DbHelper(user)
        answer = db_helper.get_search_answer(prompt=request.request)
        simple_response = response_utils.create_simple_response_from_request(request, answer)
        response = await response_utils.send_request(simple_response, "get_search_answer_service", db_provider)