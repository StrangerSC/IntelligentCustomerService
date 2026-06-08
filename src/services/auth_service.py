from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.repositories.user_repo import UserRepository
from src.schemas.user import RegisterRequest, LoginRequest
from src.utils.security import (
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
