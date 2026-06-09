import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.deps import get_current_user
from src.db.models.user import User
from src.db.session import get_db
from src.schemas.api_key import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyListResponse,
)
from src.config.settings import settings
from src.schemas.user import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from src.services import auth_service
from src.core.response import UnifiedResponse

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
    """用户登录，返回 Access Token + Refresh Token。"""
    try:
        user, access_token, refresh_token = await auth_service.login(db, data)
    except auth_service.AuthError as exc:
        return UnifiedResponse.error(
            message=exc.message, code=exc.code, status_code=exc.code
        )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user,
    )


@router.post('/refresh')
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """用 Refresh Token 换取新的 Access Token。

    无需重新登录，Refresh Token 有效期为 7 天。
    """
    try:
        new_access_token = await auth_service.refresh_access_token(
            db, data.refresh_token
        )
    except auth_service.AuthError as exc:
        return UnifiedResponse.error(
            message=exc.message, code=exc.code, status_code=exc.code
        )

    return UnifiedResponse.success(data={
        'access_token': new_access_token,
        'token_type': 'bearer',
        'expires_in': settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    })


@router.post('/api-keys', response_model=ApiKeyCreateResponse)
async def create_api_key(
    data: ApiKeyCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建第三方 API Key（需登录）。Secret 仅此次返回。"""
    ak, secret = await auth_service.create_api_key(
        db, name=data.name, user_id=current_user.id
    )
    return ApiKeyCreateResponse(
        id=ak.id,
        name=ak.name,
        api_key=ak.api_key,
        secret=secret,
    )


@router.get('/api-keys', response_model=ApiKeyListResponse)
async def list_api_keys(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查看 API Key 列表（需登录）。"""
    items, total = await auth_service.list_api_keys(
        db, page=page, page_size=page_size
    )
    return ApiKeyListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete('/api-keys/{ak_id}')
async def revoke_api_key(
    ak_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """吊销 API Key（需登录）。"""
    ok = await auth_service.revoke_api_key(db, ak_id)
    if not ok:
        return UnifiedResponse.error(
            message='API Key 不存在', code=404, status_code=404
        )
    return UnifiedResponse.success(message='已吊销')
