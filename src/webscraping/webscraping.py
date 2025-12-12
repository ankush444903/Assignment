import logging
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from clean_utils import (
    clean_soup,
    get_page_title,
    sanitize_filename,
    extract_text_segments,
    parse_html_tables,
    tables_to_tsv,
    pretty_print_tables,
)

logger = logging.getLogger(__name__)
try:
    from src.config.logging_config import setup_logging
    from src.config import settings
except Exception:
    from pathlib import Path
    from datetime import datetime
    def setup_logging(level=None, base_log_dir=None):
        import logging, os
        repo_root = Path(__file__).resolve().parents[2]
        log_root = repo_root / "src" / "logs"
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        folder = log_root / date_str
        folder.mkdir(parents=True, exist_ok=True)
        logfile = folder / f"run_{datetime.utcnow().strftime('%H%M%S')}.log"
        logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s - %(message)s")
        fh = logging.FileHandler(logfile, encoding="utf-8")
        logging.getLogger().addHandler(fh)
        return str(logfile)

    settings = type("_S", (), {"LOG_BASE_DIR": str(Path(__file__).resolve().parents[2] / "src" / "logs")})

URLS = [
"https://bankofmaharashtra.bank.in/personal-loan-for-salaried-customers",
"https://bankofmaharashtra.bank.in/maha-super-flexi-housing-loan-scheme",
"https://bankofmaharashtra.bank.in/retail-interest-rates",
"https://bankofmaharashtra.bank.in/personal-banking/loans/home-loan",
"https://bankofmaharashtra.bank.in/personal-banking/loans/personal-loan"
]

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRAPED_DIR = REPO_ROOT / "data" / "scraped_pages"
SCRAPED_DIR.mkdir(parents=True, exist_ok=True)

CLEANED_DIR = REPO_ROOT / "data" / "cleaned"
CLEANED_DIR.mkdir(parents=True, exist_ok=True)


def fetch_page(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.text


def save_raw_html(url: str, html: str):
    parsed = urlparse(url)
    name = sanitize_filename(parsed.netloc + parsed.path.replace("/", "_"))
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    file = SCRAPED_DIR / f"{name}_{ts}.html"
    file.write_text(html, encoding="utf-8")
    logger.info("Saved raw HTML to %s", file)
    return file


def write_cleaned_file(title, url, tables, segments):
    safe = sanitize_filename(title)
    file = CLEANED_DIR / f"{safe}.txt"

    lines = []
    lines.append(f"Title: {title}")
    lines.append("")  # blank line

    if tables:
        lines.append(tables_to_tsv(tables))
        lines.append(pretty_print_tables(tables))

    for seg in segments:
        lines.append(seg)

    file.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Saved cleaned text to %s", file)
    return file



def process_url(url: str):
    logger.info("Fetching %s", url)
    html = fetch_page(url)

    raw_path = save_raw_html(url, html)
    logger.info("Raw saved: %s", raw_path)

    soup = clean_soup(html)
    title = get_page_title(soup, url)
    segments = extract_text_segments(soup)
    tables = parse_html_tables(soup)

    cleaned_path = write_cleaned_file(title, url, tables, segments)
    logger.info("Cleaned saved: %s", cleaned_path)


def main():
    for url in URLS:
        process_url(url)


if __name__ == "__main__":
    logfile = setup_logging(base_log_dir=settings.LOG_BASE_DIR)
    logger.info("Starting webscraper; logfile=%s", logfile)
    main()
