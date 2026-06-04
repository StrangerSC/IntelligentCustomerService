import datetime
import logging
import os
import sys
from logging import FileHandler

from src.config.settings import settings


class DailyRotatingFileHandler(FileHandler):
    """按天轮转的日志文件处理器。

    每天自动切换日志文件，文件名格式为 YYYY-MM-DD.log，
    并自动清理超过指定保留天数的旧日志文件。
    """

    def __init__(
        self,
        log_dir: str,
        backup_days: int = 7,
        encoding: str = 'utf-8',
    ) -> None:
        """初始化处理器。

        Args:
            log_dir: 日志文件存放目录。
            backup_days: 日志保留天数，超过该天数的旧文件将被自动删除。
                默认为 7。
            encoding: 文件编码，默认为 'utf-8'。
        """
        self.log_dir = log_dir
        self.backup_days = backup_days
        self._current_date = datetime.date.today()
        filename = self._generate_filename()

        os.makedirs(log_dir, exist_ok=True)
        super().__init__(filename, encoding=encoding)
        self._cleanup_old_logs()

    def _generate_filename(self) -> str:
        """生成基于当前日期的日志文件名。

        Returns:
            绝对路径，格式为 {log_dir}/YYYY-MM-DD.log。
        """
        name = self._current_date.strftime('%Y-%m-%d') + '.log'
        return os.path.join(self.log_dir, name)

    def _cleanup_old_logs(self) -> None:
        """清理超过保留期限的旧日志文件。

        扫描日志目录中所有 *.log 文件，若文件名解析出的日期
        早于当前日期减去 backup_days，则删除该文件。
        """
        cutoff = (
            datetime.date.today()
            - datetime.timedelta(days=self.backup_days)
        )
        for filename in os.listdir(self.log_dir):
            if not filename.endswith('.log'):
                continue
            filepath = os.path.join(self.log_dir, filename)
            try:
                file_date = datetime.datetime.strptime(
                    filename.replace('.log', ''), '%Y-%m-%d'
                ).date()
                if file_date < cutoff:
                    os.remove(filepath)
            except ValueError:
                continue

    def emit(self, record: logging.LogRecord) -> None:
        """输出日志记录，并在跨天时自动切换文件。

        Args:
            record: 待输出的日志记录对象。
        """
        today = datetime.date.today()
        if today != self._current_date:
            self._current_date = today
            if self.stream:
                self.stream.close()
                self.stream = None
            self.baseFilename = self._generate_filename()
            self.stream = self._open()
            self._cleanup_old_logs()
        super().emit(record)


def setup_logging() -> None:
    """配置全局日志：同时输出到控制台与持久化文件。

    根据 settings 中配置的日志级别、目录、保留天数等参数，
    初始化根 logger，挂载控制台 Handler 与按天轮转的
    DailyRotatingFileHandler。

    Args:
        无。

    Returns:
        无。

    Note:
        函数会清空根 logger 已有的 handlers，避免重复输出。
        若日志目录无写入权限，文件 Handler 初始化将失败并被捕获，
        仅保留控制台输出，防止程序崩溃。

    Example:
        >>> from src.utils.logger import setup_logging
        >>> setup_logging()
    """
    # 计算日志绝对路径（项目根目录 / data / logs）
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )
    log_dir = os.path.join(root_dir, settings.LOG_DIR)
    os.makedirs(log_dir, exist_ok=True)

    # 日志级别
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 获取根 logger 并清空旧处理器，防止重复
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    if root_logger.handlers:
        root_logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器（按天轮转，保留 7 天）
    try:
        file_handler = DailyRotatingFileHandler(
            log_dir=log_dir,
            backup_days=settings.LOG_RETENTION_DAYS,
            encoding='utf-8',
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except (OSError, PermissionError) as exc:
        root_logger.warning(
            f'无法初始化文件日志处理器: {exc}，仅启用控制台日志。'
        )
        return

    logging.info(f'Logging initialized: console + file ({log_dir})')
