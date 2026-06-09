from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.db.models.api_key import ApiKey
from src.db.models.user import User
from src.repositories.api_key_repo import ApiKeyRepository
from src.repositories.user_repo import UserRepository
from src.schemas.user import RegisterRequest, LoginRequest
from src.core.aes_crypto import encrypt_secret
from src.utils.api_key import generate_api_key, generate_secret
from src.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class AuthError(Exception):
    """认证异常。"""

    def __init__(self, message: str, code: int = 400) -> None:
        self.message = message
        self.code = code


async def register(db: AsyncSession, data: RegisterRequest) -> User:
    """用户注册。

    校验账号和手机号唯一性，密码哈希后写入数据库。

    Args:
        db: 异步数据库会话。
        data: 注册请求体。

    Returns:
        新创建的用户实例。

    Raises:
        AuthError: 账号或手机号已存在。
    """
    repo = UserRepository(db)

    if await repo.find_by_account(data.account):
        raise AuthError('账号已存在')

    if await repo.find_by_phone(data.phone_number):
        raise AuthError('手机号已注册')

    user = User(
        account=data.account,
        phone_number=data.phone_number,
        password=hash_password(data.password),
    )
    return await repo.insert(user)


async def login(db: AsyncSession, data: LoginRequest) -> tuple[User, str]:
    """用户登录，验证通过后颁发 JWT。

    校验账号是否存在、密码是否匹配、账号状态是否正常。

    Args:
        db: 异步数据库会话。
        data: 登录请求体。

    Returns:
        (用户实例, JWT 令牌)

    Raises:
        AuthError: 账号不存在、密码错误、账号已冻结或已禁用。
    """
    repo = UserRepository(db)

    user = await repo.find_by_account(data.account)
    if not user:
        raise AuthError('账号或密码错误', code=401)

    if not verify_password(data.password, user.password):
        raise AuthError('账号或密码错误', code=401)

    if user.is_frozen:
        raise AuthError('账号已冻结，请联系客服', code=403)

    if not user.is_enabled:
        raise AuthError('账号已禁用', code=403)

    token = create_access_token(user_id=str(user.id))
    return user, token


async def create_api_key(db: AsyncSession, name: str, user_id: UUID) -> tuple[ApiKey, str]:
    """创建第三方 API Key + Secret。

    Secret 仅在此时返回明文，AES-256-GCM 加密后存入数据库。

    Args:
        db: 异步数据库会话。
        name: 备注名称。
        user_id: 创建人用户 ID。

    Returns:
        (ApiKey 实例, 明文 Secret)
    """
    repo = ApiKeyRepository(db)
    api_key = generate_api_key()
    secret = generate_secret()

    ak = ApiKey(
        name=name,
        api_key=api_key,
        secret=encrypt_secret(secret),
        created_by=str(user_id),
    )
    await repo.insert(ak)
    return ak, secret


async def list_api_keys(
    db: AsyncSession, page: int = 1, page_size: int = 20
) -> tuple[list[ApiKey], int]:
    """分页查询 API Key 列表。"""
    repo = ApiKeyRepository(db)
    return await repo.find_all(page=page, page_size=page_size)


async def revoke_api_key(db: AsyncSession, ak_id) -> bool:
    """吊销 API Key（软删除）。"""
    repo = ApiKeyRepository(db)
    return await repo.soft_delete(ak_id)
