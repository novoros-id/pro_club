import uuid
from pydantic import BaseModel


class CodeUID(BaseModel):
    username: str
    program_uid: str
    request_uid: str

class AnyRequestBase(BaseModel):
    code_uid: CodeUID
    
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