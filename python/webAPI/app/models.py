import uuid
from pydantic import BaseModel

""" class AnyRequest(UserBase): """


class UserCheck(BaseModel):
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

class Question(BaseModel):
    user_id: str
    prompt: str

class QuestionPublic(BaseModel):
    user_id: str
    answer: str