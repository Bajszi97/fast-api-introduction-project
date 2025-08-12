from typing import Annotated
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