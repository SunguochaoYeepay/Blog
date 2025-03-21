from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: str = Field(..., description="全名")
    department: Optional[str] = Field(None, description="部门")
    role: Optional[str] = Field(None, description="角色")
    avatar: Optional[str] = Field(None, description="头像")
    is_active: Optional[bool] = Field(True, description="是否激活")
    is_superuser: Optional[bool] = Field(False, description="是否超级管理员")

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str = Field(..., description="密码")

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, description="全名")
    department: Optional[str] = Field(None, description="部门")
    role: Optional[str] = Field(None, description="角色")
    password: Optional[str] = Field(None, description="密码")
    avatar: Optional[str] = Field(None, description="头像")
    phone: Optional[str] = Field(None, description="电话")
    bio: Optional[str] = Field(None, description="个人简介")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_superuser: Optional[bool] = Field(None, description="是否超级管理员")

    model_config = ConfigDict(from_attributes=True)

class UserUpdateMe(BaseModel):
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, description="全名")

class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    phone: Optional[str] = Field(None, description="电话")
    bio: Optional[str] = Field(None, description="个人简介")
    last_login: Optional[datetime] = None
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    articles_count: Optional[int] = Field(0, description="文章数量")
    comments_count: Optional[int] = Field(0, description="评论数量")
    
    model_config = ConfigDict(from_attributes=True)

class UserQuery(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None

class UserInDBBase(UserBase):
    id: int = Field(..., description="用户ID")
    is_active: bool = Field(..., description="是否激活")
    is_superuser: bool = Field(..., description="是否超级管理员")

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str = Field(..., description="哈希密码")

class UserOut(UserInDBBase):
    pass

class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")