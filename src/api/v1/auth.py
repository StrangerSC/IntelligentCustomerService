from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.schemas.user import (
    RegisterRequest,
    LoginRequest,
    UserOut,
    TokenResponse,
)
from src.services import auth_service
from src.utils.response import UnifiedResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=UserOut)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """用户注册。"""
    try:
        user = await auth_service.register(db, data)
    except auth_service.AuthError as exc:
        return UnifiedResponse.error(
            message=exc.message, code=exc.code, status_code=exc.code
        )
    return user


@router.post('/login', response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """用户登录，返回 JWT 令牌。"""
    try:
        user, token = await auth_service.login(db, data)
    except auth_service.AuthError as exc:
        return UnifiedResponse.error(
            message=exc.message, code=exc.code, status_code=exc.code
        )

    return TokenResponse(token=token, user=user)
