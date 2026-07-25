from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True