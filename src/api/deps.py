import uuid

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.db.session import get_db
from src.repositories.user_repo import UserRepository
from src.utils.security import decode_access_token

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从请求头 JWT 中解析当前登录用户。

    从 Authorization: Bearer <token> 中提取 JWT，
    解码后查询数据库返回用户实例。

    Args:
        credentials: HTTPBearer 自动解析的认证凭证。
        db: 异步数据库会话。

    Returns:
        当前登录用户实例。

    Raises:
        HTTPException 401: token 无效或已过期。
        HTTPException 401: 用户不存在或已删除。
        HTTPException 403: 用户已冻结或已禁用。
    """
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail='令牌无效或已过期')

    user_id = payload.get('sub')
    if user_id is None:
        raise HTTPException(status_code=401, detail='令牌格式错误')

    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail='令牌格式错误')

    repo = UserRepository(db)
    user = await repo.find_by_id(uid)
    if user is None:
        raise HTTPException(status_code=401, detail='用户不存在')

    if user.is_frozen:
        raise HTTPException(status_code=403, detail='账号已冻结')

    if not user.is_enabled:
        raise HTTPException(status_code=403, detail='账号已禁用')

    return user
