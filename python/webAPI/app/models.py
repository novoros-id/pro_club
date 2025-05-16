from pydantic import BaseModel, field_validator


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
    name: str
    email: str | None = None

    class Config:
        from_attributes = True

class CreateUser(SimpleRequest):
    user: UserBase

class ProgramConnectionBase(BaseModel):
    program_uid: str
    name: str | None = None
    clienttype: str
    description: str | None = None
    url: str
    client_login: str | None = None
    client_pass: str | None = None
    endpoint: str | None = None

    @field_validator("description", "client_login", "client_pass", "endpoint",  mode="before")
    def replace_none_with_empty_string(cls, value):
        return value if value is not None else ""

class CreateProgramConnection(SimpleRequest, ProgramConnectionBase):
    pass
