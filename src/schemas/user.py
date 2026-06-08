import uuid
from typing import Optional

from pydantic import BaseModel, Field, field_validator
import re


class RegisterRequest(BaseModel):
    """注册请求体。"""

    account: str = Field(
        ..., min_length=4, max_length=30, description='登录账号'
    )
    phone_number: str = Field(
        ..., min_length=11, max_length=20, description='手机号'
    )
    password: str = Field(
        ..., min_length=6, max_length=72, description='登录密码'
    )

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """校验手机号格式。"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class LoginRequest(BaseModel):
    """登录请求体。"""

    account: str = Field(..., description='登录账号')
    password: str = Field(..., description='登录密码')


class UserOut(BaseModel):
    """用户响应模型。"""

    id: uuid.UUID
    account: str
    phone_number: str
    is_enabled: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """登录成功返回的令牌。"""

    token: str
    user: UserOut
