import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class LoggerBase(ABC):
    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None: ...

    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None: ...

    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None: ...

    @abstractmethod
    def error(self, message: str, **kwargs: Any) -> None: ...


class BasicLogger(LoggerBase):
    """
    Lightweight structured logger that wraps `logging.Logger` and emits JSON lines.
    Fields: timestamp, level, name, message, and optional extras.
    """

    def __init__(self, name: str = __name__, level: int = logging.INFO) -> None:
        self._name = name
        self._logger = logging.getLogger(name)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            self._logger.addHandler(handler)
        self._logger.setLevel(level)

    def _emit(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        payload: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "name": self._name,
            "message": message,
        }
        if extra:
            payload.update(extra)
        line = json.dumps(payload, ensure_ascii=False)
        # Route through standard logger to respect handlers/levels
        if level == "DEBUG":
            self._logger.debug(line)
        elif level == "INFO":
            self._logger.info(line)
        elif level == "WARNING":
            self._logger.warning(line)
        else:
            self._logger.error(line)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._emit("DEBUG", message, kwargs or None)

    def info(self, message: str, **kwargs: Any) -> None:
        self._emit("INFO", message, kwargs or None)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._emit("WARNING", message, kwargs or None)

    def error(self, message: str, **kwargs: Any) -> None:
        self._emit("ERROR", message, kwargs or None)


def get_logger(name: str) -> BasicLogger:
    return BasicLogger(name=name)

