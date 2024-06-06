from typing import Optional
from pydantic import BaseModel

class MessageRequest(BaseModel):
    message: str

# Modelos Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    id: str
    email: str
    phone: str
    name: str


class UserInDB(User):
    password: str
