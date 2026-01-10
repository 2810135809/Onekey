"""日志模块"""

import sys
from loguru import logger

from .constants import LOG_DIR


class Logger:
    """统一的日志管理器"""

    def __init__(self, name: str, debug_mode: bool = False, log_file: bool = True):
        self.name = name
        self.debug_mode = debug_mode
        self.log_file = log_file
        self._setup_logger()
        self._logger = logger.bind(name=name)

    def _setup_logger(self):
        """设置日志器"""
        # 移除默认的 handler
        logger.remove()

        level = "DEBUG" if self.debug_mode else "INFO"

        # 控制台输出
        logger.add(
            sys.stderr, format="<level>{message}</level>", level=level, colorize=True
        )

        if self.log_file:
            LOG_DIR.mkdir(exist_ok=True)
            logfile = LOG_DIR / f"{self.name}.log"

            # 文件输出
            file_format = (
                "[{time:YYYY-MM-DD HH:mm:ss}] | "
                "[{extra[name]}:{level}] | "
                "[{module}.{function}:{line}] - {message}"
            )

            logger.add(
                logfile,
                format=file_format,
                level=level,
                encoding="utf-8",
                filter=lambda record: record["extra"].get("name") == self.name,
            )

    def debug(self, msg: str):
        self._logger.opt(depth=1).debug(msg)

    def info(self, msg: str):
        self._logger.opt(depth=1).info(msg)

    def warning(self, msg: str):
        self._logger.opt(depth=1).warning(msg)

    def error(self, msg: str):
        self._logger.opt(depth=1).error(msg)

    def critical(self, msg: str):
        self._logger.opt(depth=1).critical(msg)
