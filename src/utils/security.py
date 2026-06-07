from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=14)


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希。

    Args:
        password: 明文密码。

    Returns:
        bcrypt 哈希后的密文（60 字符左右）。
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