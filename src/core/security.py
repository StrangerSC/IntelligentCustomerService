from datetime import datetime, timedelta, timezone
from pathlib import Path

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config.settings import BASE_DIR, settings

pwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto',
    bcrypt__rounds=14,
)


def _load_key(path: str) -> str:
    """从文件读取密钥内容。

    Args:
        path: 相对于项目根目录的密钥文件路径，或绝对路径。

    Returns:
        密钥文件内容（字符串）。
    """
    if not Path(path).is_absolute():
        path = str(BASE_DIR / path)
    return Path(path).read_text(encoding='utf-8')


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希。

    bcrypt 上限 72 字节，超出部分自动截断。

    Args:
        password: 明文密码。

    Returns:
        bcrypt 哈希后的密文（60 字符左右）
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否与哈希值匹配。

    Args:
        plain_password: 用户输入的明文密码。
        hashed_password: 数据库中存储的哈希密码。

    Returns:
        True 表示匹配，False 表示不匹配。
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    """签发 JWT 访问令牌（短期，仅用于 API 调用）。

    Args:
        user_id: 用户 UUID 字符串。
        expires_delta: 过期时间偏移量，None 则从配置读取。

    Returns:
        编码后的 JWT 字符串。
    """
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        'sub': user_id,
        'iat': now,
        'exp': expire,
        'type': 'access',
    }

    key = _load_key(settings.JWT_PRIVATE_KEY_PATH)
    return jwt.encode(payload, key, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    """签发 JWT 刷新令牌（长期，仅用于换取新 Access Token）。

    Args:
        user_id: 用户 UUID 字符串。
        expires_delta: 过期时间偏移量，None 则从配置读取（默认 7 天）。

    Returns:
        编码后的 JWT 字符串。
    """
    if expires_delta is None:
        expires_delta = timedelta(
            hours=settings.REFRESH_TOKEN_EXPIRE_HOURS
        )

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        'sub': user_id,
        'iat': now,
        'exp': expire,
        'type': 'refresh',
    }

    key = _load_key(settings.JWT_PRIVATE_KEY_PATH)
    return jwt.encode(payload, key, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """解码 JWT 访问令牌，仅接受 type=access 的令牌。

    刷新令牌（type=refresh）不能用于 API 调用。

    Args:
        token: JWT 字符串。

    Returns:
        解码后的 payload 字典；解码失败或类型不匹配返回 None。
    """
    key = _load_key(settings.JWT_PUBLIC_KEY_PATH)
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None
    if payload.get('type') != 'access':
        return None
    return payload


def decode_refresh_token(token: str) -> dict | None:
    """解码 JWT 刷新令牌，仅接受 type=refresh 的令牌。

    Access Token 不能用于刷新。

    Args:
        token: JWT 字符串。

    Returns:
        解码后的 payload 字典；解码失败或类型不匹配返回 None。
    """
    key = _load_key(settings.JWT_PUBLIC_KEY_PATH)
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None
    if payload.get('type') != 'refresh':
        return None
    return payload