import uuid
from pydantic import BaseModel

class AnyRequestBase(BaseModel):
    username: str
    program_uid: str
    request_uid: str
class SimpleRequest(AnyRequestBase):
    request : str | None = None

class SimpleResponse(AnyRequestBase):
    answer: str | None = None

class UserBase(BaseModel):
    id: str
    username: str


""" class UserRequest(AnyRequestBase):
    pass """


""" class StatusResponse(AnyRequestBase):
    status: str """


""" 
class Question(BaseModel):
    user_id: str
    prompt: str

class QuestionPublic(BaseModel):
    user_id: str
    answer: str  """