
from urllib.parse import urlparse
from typing import Optional


def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc

        if ":" in netloc:
            netloc = netloc.split(":")[0]

        if netloc.startswith("www."):
            netloc = netloc[4:]

        return netloc
    except Exception:
        return url


def normalize_url_for_db(url: str) -> str:

    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path or ""
        query = f"?{parsed.query}" if parsed.query else ""
        return f"{parsed.scheme}://{netloc}{path}{query}"
    except Exception:
        return url