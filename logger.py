from datetime import datetime, timezone
import logging ,json ,sys


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            # 必定存在
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),

            # 商業應用
            "service": getattr(record, "service", "unknown"),
            "stage": getattr(record, "stage", "unknown"),
            "status": getattr(record, "status", "unknown"),
            
        }
        return json.dumps(log_record, ensure_ascii=False)


def get_logger(
    service: str = "etl",
    stage: str = "local"):
    
    logger = logging.getLogger("etl_logger")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    # 🔑 預設 context（確保不傳 extra 也不會缺）
    logger = logging.LoggerAdapter(
        logger,
        {
            "service": service,
            "stage": stage,
            "status": "ok",  # 預設狀態
        },
    )

    return logger
