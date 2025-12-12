import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
import os


def setup_logging(level: str = None, base_log_dir: str = None):
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")

    if base_log_dir:
        log_root = Path(base_log_dir)
    else:
        repo_root = Path(__file__).resolve().parents[2]
        log_root = repo_root / "src" / "logs"


    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    time_str = datetime.utcnow().strftime("%H%M%S")
    folder = log_root / date_str
    folder.mkdir(parents=True, exist_ok=True)

    logfile = folder / f"run_{time_str}.log"


    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(getattr(logging, level.upper(), logging.INFO))


        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, level.upper(), logging.INFO))
        ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))
        root.addHandler(ch)


        fh = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
        fh.setLevel(getattr(logging, level.upper(), logging.INFO))
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))
        root.addHandler(fh)


        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("langchain").setLevel(logging.WARNING)
        logging.getLogger("langchain_core").setLevel(logging.WARNING)
        logging.getLogger("langchain_openai").setLevel(logging.WARNING)

    return str(logfile)
