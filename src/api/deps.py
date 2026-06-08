import uuid

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.api_key import ApiKey
from src.db.models.user import User
from src.db.session import get_db
from src.repositories.api_key_repo import ApiKeyRepository
from src.repositories.user_repo import UserRepository
from src.utils.aes_crypto import decrypt_secret
from src.utils.api_key import verify_signature
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


async def get_current_third_party(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    """第三方 API Key + HMAC 签名认证。

    从请求头提取 X-API-Key、X-Timestamp、X-Signature，
    校验 HMAC-SHA256 签名后返回对应的 ApiKey 记录。

    Args:
        request: FastAPI Request 对象。
        db: 异步数据库会话。

    Returns:
        认证通过的 ApiKey 实例。

    Raises:
        HTTPException 401: API Key 无效、签名错误或时间戳过期。
        HTTPException 403: API Key 已禁用。
    """
    api_key = request.headers.get('X-API-Key')
    timestamp = request.headers.get('X-Timestamp')
    signature = request.headers.get('X-Signature')

    if not api_key or not timestamp or not signature:
        raise HTTPException(status_code=401, detail='缺少认证头')

    repo = ApiKeyRepository(db)
    ak = await repo.find_by_key(api_key)
    if ak is None:
        raise HTTPException(status_code=401, detail='API Key 无效')

    if not ak.is_enabled:
        raise HTTPException(status_code=403, detail='API Key 已禁用')

    # 验签：先解密 Secret，再算 HMAC
    body = await request.body()
    if not verify_signature(decrypt_secret(ak.secret), body, timestamp, signature):
        raise HTTPException(status_code=401, detail='签名验证失败')

    return ak
