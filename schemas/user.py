from pydantic import BaseModel

class UserBase(BaseModel):
    first_name: str
    last_name: str
    login: str
    email: str

class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    login: str
    password: str

class ChangePassword(BaseModel):
    password: str
    new_password: str
    confirm_new_password: str

class ChangeLogin(BaseModel):
    new_login: str
    