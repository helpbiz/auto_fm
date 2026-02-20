# src/logging_config.py
"""
앱 전용 로거: logs/app.log 에 집계 수식·결과 기록.
Zero Script QA를 위한 JSON 구조화 로깅 지원.
"""
import json
import logging
from datetime import datetime
from typing import Any

from src.utils.path_helper import get_logs_dir


class JsonFormatter(logging.Formatter):
    """JSON 형식 로그 포매터 (Zero Script QA 호환)"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "service": "auto_fm",
            "message": record.getMessage(),
        }

        # 추가 데이터가 있으면 포함
        if hasattr(record, "data") and record.data:
            log_entry["data"] = record.data

        # 에러인 경우 스택 트레이스 포함
        if record.exc_info:
            log_entry["error"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


def setup_app_logger(json_format: bool = True) -> logging.Logger:
    """logs/app.log 에 INFO 이상 기록하는 'app' 로거 설정.

    Args:
        json_format: True면 JSON 형식, False면 기존 텍스트 형식 (기본값: True)
    """
    log_dir = get_logs_dir()
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)

    if not app_logger.handlers:
        fh = logging.FileHandler(log_dir / "app.log", encoding="utf-8-sig")

        if json_format:
            fh.setFormatter(JsonFormatter())
        else:
            fh.setFormatter(
                logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )

        app_logger.addHandler(fh)

    return app_logger


def log_with_data(logger: logging.Logger, level: int, message: str, data: dict[str, Any] = None) -> None:
    """데이터와 함께 로그 기록 (Zero Script QA용)

    Example:
        log_with_data(logger, logging.INFO, "계산 완료", {
            "scenario_id": "시나리오1",
            "labor_total": 1500000,
            "overhead_rate": 10,
            "duration_ms": 125
        })
    """
    extra = {"data": data} if data else {}
    logger.log(level, message, extra=extra)
