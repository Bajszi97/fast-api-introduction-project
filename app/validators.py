from typing import Annotated, Optional
from pydantic import BaseModel, Field, model_validator


class CreateUserRequest(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=64)]
    password: Annotated[str, Field(min_length=8)]
    password_confirm: Annotated[str, Field(min_length=8)]

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class CreateUserResponse(BaseModel):
    id: int
    username: str
    created_at: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    token: str


class CreateProjectRequest(BaseModel):
    name: Annotated[str, Field(max_length=128)]
    description: Optional[str] = None


class CreateProjectResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str
