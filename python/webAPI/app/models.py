import uuid
from pydantic import BaseModel

class AnyRequestBase(BaseModel):
    username: str
    program_uid: str
    request_uid: str

class UserRequest(AnyRequestBase):
    pass

class UserBase(BaseModel):
    username: str

""" class UserCheck(BaseModel):
    id: str
    name: str

class UserBase(BaseModel):
    id: str
    name: str
    email: str | None

class UserPublic(BaseModel):
    id: str
    name: str
    email: str | None
"""

class Question(BaseModel):
    user_id: str
    prompt: str

class QuestionPublic(BaseModel):
    user_id: str
    answer: str 