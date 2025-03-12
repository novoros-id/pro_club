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