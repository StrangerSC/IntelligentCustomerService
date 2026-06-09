from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """应用配置类。

    从环境变量及 .env 文件读取配置，支持类型校验与默认值。
    """

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / '.env'),
        env_file_encoding='utf-8',
        extra='ignore',
    )

    # 应用基础配置
    APP_NAME: str = 'IntelligentCustomerService'
    DEBUG: bool = False
    HOST: str = ''
    PORT: int

    # API 配置
    API_V1_PREFIX: str = ''

    # CORS 配置
    CORS_ORIGINS: list[str] = []

    # --- LLM 配置 (国产模型) ---
    # 百度千帆平台
    API_KEY: str = ''
    BASE_URL: str = ''
    MODEL: str = ''

    # 数据库基础配置
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # 通过 @property 动态构建数据库 URL
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # --- Embedding 配置 ---
    EMBEDDING_PATH: str = ''

    # --- 安全配置 ---
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_HOURS: int = 168           # 7 天
    JWT_ALGORITHM: str = 'RS256'
    JWT_PRIVATE_KEY_PATH: str = ''                   # RSA 私钥文件路径
    JWT_PUBLIC_KEY_PATH: str = ''                    # RSA 公钥文件路径
    AES_KEY_PATH: str = ''                           # AES-256 密钥文件路径
    MAX_FAILED_LOGIN_ATTEMPTS: int = 3               # 最多允许的失败次数
    FAILED_LOGIN_WINDOW_MINUTES: int = 5             # 失败计数窗口（分钟）

    # --- Redis 配置 ---
    REDIS_URL: str = ''                              # 为空时自动使用本地内存缓存（开发模式）

    # --- 日志配置 ---
    LOG_LEVEL: str = 'INFO'
    LOG_DIR: str = 'data/logs'
    LOG_RETENTION_DAYS: int = 7


settings = Settings()
