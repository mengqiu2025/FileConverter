import logging
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def configure_logging(app_dir):
    log_dir = Path(app_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("file_converter")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    handler = TimedRotatingFileHandler(
        log_dir / "converter.log",
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(handler)
    return logger


def cleanup_old_logs(log_dir, retention_days=30):
    log_dir = Path(log_dir)
    if not log_dir.exists():
        return
    cutoff = time.time() - retention_days * 24 * 3600
    for path in log_dir.glob("*.log*"):
        if path.is_file() and path.stat().st_mtime < cutoff:
            path.unlink()
