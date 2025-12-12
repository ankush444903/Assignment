import re
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def remove_footer_by_heuristic(soup: BeautifulSoup) -> None:
    for tag in soup.find_all("footer"):
        try:
            tag.decompose()
        except Exception:
            pass

    pattern = re.compile(r"footer", re.I)
    for el in soup.find_all(attrs={"id": pattern}):
        try:
            el.decompose()
        except Exception:
            pass
    for el in soup.find_all(attrs={"class": pattern}):
        try:
            el.decompose()
        except Exception:
            pass

    for el in soup.find_all(attrs={"role": "contentinfo"}):
        try:
            el.decompose()
        except Exception:
            pass

    copyright_markers = re.compile(
        r"©|copyright|all rights reserved|privacy policy|terms of use|powered by",
        re.I,
    )
    for el in soup.find_all(string=copyright_markers):
        parent = el.find_parent()
        if parent:
            candidate = parent
            for _ in range(4):
                if candidate.name in ("div", "footer", "section", "aside", "nav", "article"):
                    break
                if candidate.parent is None:
                    break
                candidate = candidate.parent
            try:
                candidate.decompose()
            except Exception:
                pass

    for el in soup.find_all(style=True):
        style = el.get("style", "").replace(" ", "").lower()
        if ("position:fixed" in style or "position:sticky" in style) and "bottom" in style:
            try:
                el.decompose()
            except Exception:
                pass

    for block in soup.find_all(["div", "section", "nav", "aside"]):
        try:
            text = (block.get_text(strip=True) or "")
            links = block.find_all("a")
            if links and len(text) < 200 and len(links) >= 3:
                block.decompose()
        except Exception:
            pass


def clean_soup(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, "html.parser")

    for tag_name in ("script", "style", "noscript"):
        for tag in soup.find_all(tag_name):
            tag.decompose()

    for selector in ("header", "nav", "aside", ".navbar", ".breadcrumb", "#cookieConsent"):
        for tag in soup.select(selector):
            tag.decompose()

    remove_footer_by_heuristic(soup)
    return soup


def get_page_title(soup: BeautifulSoup, url: str) -> str:
    main = soup.find("main") or soup
    h1 = main.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    parsed = urlparse(url)
    return parsed.path.strip("/") or parsed.netloc


def sanitize_filename(s: str, max_len: int = 100) -> str:
    s = s.strip()
    s = re.sub(r"[^\w\-_\. ]", "_", s)
    s = re.sub(r"\s+", "_", s)
    return s[:max_len]


def extract_text_segments(soup: BeautifulSoup) -> List[str]:
    main = soup.find("main") or soup.body or soup
    raw_text = main.get_text(separator="\n")
    segments: List[str] = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or len(line) < 3:
            continue
        segments.append(line)

    seen = set()
    out: List[str] = []
    for seg in segments:
        if seg not in seen:
            seen.add(seg)
            out.append(seg)
    return out


def parse_html_tables(soup: BeautifulSoup) -> List[List[List[str]]]:
    main = soup.find("main") or soup.body or soup
    tables = []
    for tbl in main.find_all("table"):
        rows = []
        for tr in tbl.find_all("tr"):
            cells = []
            for cell in tr.find_all(["th", "td"]):
                text = " ".join(cell.get_text(separator=" ", strip=True).split())
                cells.append(text)
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def tables_to_tsv(tables):
    parts = []
    for i, table in enumerate(tables, start=1):
        parts.append(f"--- TABLE {i} (TSV) ---")
        for row in table:
            parts.append("\t".join(row))
        parts.append("")
    return "\n".join(parts)


def pretty_print_tables(tables):
    out_lines = []
    for i, table in enumerate(tables, start=1):
        out_lines.append(f"=== TABLE {i} (pretty) ===")
        max_cols = max(len(r) for r in table)
        col_widths = [0] * max_cols

        for r in table:
            for idx in range(max_cols):
                cell = r[idx] if idx < len(r) else ""
                col_widths[idx] = max(col_widths[idx], len(cell))

        for r in table:
            padded = []
            for idx in range(max_cols):
                cell = r[idx] if idx < len(r) else ""
                padded.append(cell.ljust(col_widths[idx]))
            out_lines.append(" | ".join(padded))
        out_lines.append("")
    return "\n".join(out_lines)
