from typing import Any


def singleton(class_: Any) -> Any:
    instances = {}

    def getinstance(*args: Any, **kwargs: Any) -> Any:
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance
