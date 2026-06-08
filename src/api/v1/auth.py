import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.db.models.user import User
from src.db.session import get_db
from src.schemas.api_key import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyListResponse,
)
from src.schemas.user import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
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


@router.post('/api-keys', response_model=ApiKeyCreateResponse)
async def create_api_key(
    data: ApiKeyCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建第三方 API Key（需登录）。Secret 仅此次返回。"""
    ak, secret = await auth_service.create_api_key(
        db, name=data.name, id=current_user.id
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
