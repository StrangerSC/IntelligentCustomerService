import base64
import os
import secrets
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.config.settings import BASE_DIR, settings


def _load_key() -> bytes:
    """加载 AES 密钥文件。"""
    path = settings.AES_KEY_PATH
    if not Path(path).is_absolute():
        path = str(BASE_DIR / path)
    return bytes.fromhex(Path(path).read_text(encoding='utf-8').strip())


def encrypt_secret(plaintext: str) -> str:
    """AES-256-GCM 加密 Secret。

    Args:
        plaintext: 明文 Secret。

    Returns:
        base64 编码的密文（含 IV + 密文 + 认证标签）。
    """
    key = _load_key()
    nonce = secrets.token_bytes(12)
    aesgcm = AESGCM(key)

    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    # IV(12) + ciphertext + tag(16)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt_secret(encrypted: str) -> str:
    """AES-256-GCM 解密 Secret。

    Args:
        encrypted: base64 编码的密文。

    Returns:
        明文 Secret。
    """
    key = _load_key()
    raw = base64.b64decode(encrypted)
    nonce = raw[:12]
    ciphertext = raw[12:]

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()
