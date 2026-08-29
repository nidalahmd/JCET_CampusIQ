import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.entities import UserRole


class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Full name of user")
    email: EmailStr = Field(..., description="Institutional or personal email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 characters)")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role: student or admin")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Password")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Updated full name")


class ChangePassword(BaseModel):
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password (min 8 characters)")
