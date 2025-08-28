from typing import Annotated, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator


class CreateUserRequest(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=64)]
    password: Annotated[str, Field(min_length=8)]
    password_confirm: Annotated[str, Field(min_length=8)]

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    token: str


class CreateProjectRequest(BaseModel):
    name: Annotated[str, Field(max_length=128)]
    description: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



class AddParticipantRequest(BaseModel):
    user_id: int


class UploadedDocument(BaseModel):
    filename: Optional[Annotated[str, Field(min_length=1, max_length=256)]]
    content_type: Optional[Annotated[str, Field(min_length=1, max_length=64)]]
    content: bytes     


class ProjectDocumentOut(BaseModel):
    id: int
    project_id: int
    filename: str
    file_type: str
    created_at: datetime
    url:  str
