from typing import Optional
from pydantic import BaseModel, EmailStr

class StateRequest(BaseModel):
    user_id: int
    user_name: str

class MessageRequest(BaseModel):
    message: str
    user_phone: str

# Modelos Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    id: int
    email: str
    phone: str
    name: str

    class Config:
        from_attributes=True


class UserInDB(User):
    password: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str

class InfoCreate(BaseModel):
    user_id: int
    title: str
    content: str
    
class InfoResponse(BaseModel):
    id: int
    title:str
    content:str

    class Config:
        orm_mode=True