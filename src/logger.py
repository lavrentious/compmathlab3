from enum import Enum
from io import TextIOWrapper
from typing import Any

from utils.meta import singleton


class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


def log_level_to_str(level: LogLevel) -> str:
    return level.name


class Logger:
    file: None | TextIOWrapper | Any
    min_level = LogLevel.INFO

    def __init__(
        self,
        file: None | TextIOWrapper | Any = None,
        min_level: LogLevel = LogLevel.INFO,
    ) -> None:
        self.file = file
        self.min_level = min_level

    def set_min_level(self, min_level: LogLevel) -> None:
        self.min_level = min_level

    def log(
        self,
        *args: Any,
        level: LogLevel = LogLevel.INFO,
        sep: str = " ",
        end: str = "\n",
    ) -> None:
        if level.value < self.min_level.value:
            return
        print(f"[{log_level_to_str(level)}]", *args, sep=sep, end=end, file=self.file)

    def debug(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        self.log(*args, level=LogLevel.DEBUG, sep=sep, end=end)

    def info(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        self.log(*args, level=LogLevel.INFO, sep=sep, end=end)

    def warning(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        self.log(*args, level=LogLevel.WARNING, sep=sep, end=end)

    def error(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        self.log(*args, level=LogLevel.ERROR, sep=sep, end=end)

    def critical(self, *args: Any, sep: str = " ", end: str = "\n") -> None:
        self.log(*args, level=LogLevel.CRITICAL, sep=sep, end=end)


@singleton
class GlobalLogger(Logger):
    pass
