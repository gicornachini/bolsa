from typing import Any, Dict


class SingletonCreateMixin:

    _instances: Dict[Any, Any] = {}

    @classmethod
    def create(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = cls(*args, **kwargs)
        return cls._instances[cls]
