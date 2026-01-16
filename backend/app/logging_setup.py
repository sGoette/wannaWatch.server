import logging
import logging.config
from pathlib import Path

def setup_logging(log_path: Path, level: str = "INFO") -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "version": 1,
        "disable_existing_loggers": False,  # keep library loggers working
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(levelname)s %(name)s: %(message)s"
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_path,
                "maxBytes": 5_000_000,
                "backupCount": 5,
                "mode": "a",
                "encoding": "utf-8",
                "formatter": "standard",
                "level": level,
            },
        },
        "root": {  # catch-all
            "handlers": ["file"],
            "level": level,
        },
        "loggers": {
            # Uvicorn / FastAPI server logs
            "uvicorn": {"level": level, "propagate": True},
            "uvicorn.error": {"level": level, "propagate": True},
            "uvicorn.access": {"level": level, "propagate": True},

            # FastAPI / Starlette internals (usually propagate via root, but ok to include)
            "fastapi": {"level": level, "propagate": True},
            "starlette": {"level": level, "propagate": True},

            # aiosqlite (if it logs in your setup)
            "aiosqlite": {"level": level, "propagate": True},

            # If you use SQLAlchemy async:
            # "sqlalchemy.engine": {"level": "INFO", "propagate": True},
        },
    }
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.config.dictConfig(config)
