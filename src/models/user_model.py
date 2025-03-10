from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str = None
    disabled: bool = False

    class Config:
        orm_mode = True