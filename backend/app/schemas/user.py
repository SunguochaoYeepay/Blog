from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    department: str
    role: str

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str
    avatar: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserQuery(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None