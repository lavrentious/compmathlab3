import traceback
from typing import Any

from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import Python3TracebackLexer


def singleton(class_: Any) -> Any:
    instances = {}

    def getinstance(*args: Any, **kwargs: Any) -> Any:
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def colorful_error_trace(e: Exception) -> str:
    return "".join(
        [
            highlight(line, Python3TracebackLexer(), TerminalTrueColorFormatter())
            for line in traceback.format_tb(e.__traceback__)
        ]
    )
