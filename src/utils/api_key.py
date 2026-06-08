import base64
import hashlib
import hmac
import secrets
import time


def generate_api_key() -> str:
    """生成 API Key（ak_ 前缀 + 32 位十六进制随机串）。

    Returns:
        例如 ``ak_a1b2c3d4e5f6...``
    """
    return 'ak_' + secrets.token_hex(32)


def generate_secret() -> str:
    """生成 API Secret（sk_ 前缀 + 64 位十六进制随机串）。

    Returns:
        例如 ``sk_a1b2c3d4...``
    """
    return 'sk_' + secrets.token_hex(64)


def verify_signature(
    secret: str,
    body: bytes,
    timestamp: str,
    signature: str,
    max_age_seconds: int = 300,
) -> bool:
    """校验 HMAC-SHA256 签名。

    Args:
        secret: 原始 Secret（明文，不是哈希）。
        body: HTTP 请求体原始字节。
        timestamp: X-Timestamp 头值。
        signature: X-Signature 头值（base64 编码）。
        max_age_seconds: 时间戳最大有效秒数，默认 300（5 分钟）。

    Returns:
        True 表示签名有效，False 表示无效或过期。
    """
    # 防重放：时间戳过期
    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        return False

    if abs(int(time.time()) - ts) > max_age_seconds:
        return False

    # 计算期望签名：HMAC-SHA256(body + timestamp, secret)
    message = body + timestamp.encode()
    expected = hmac.new(
        secret.encode(),
        message,
        hashlib.sha256,
    ).digest()
    expected_b64 = base64.b64encode(expected).decode()

    return hmac.compare_digest(expected_b64, signature)
