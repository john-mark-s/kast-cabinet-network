"""
Utility functions for Kast Cabinet Network scrapers.

Provides:
- RUT normalization and validation (módulo 11)
- API retry wrapper using tenacity
- Date helpers
"""

import os
import re
import time
import logging
from typing import Any, Dict, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# RUT helpers
# ---------------------------------------------------------------------------

def normalize_rut(rut: str) -> str:
    """
    Strip dots and spaces; ensure format is '12345678-9'.
    Handles inputs like '12.345.678-9', '12345678-9', '12345678 9', '123456789'.
    """
    if not rut:
        return rut
    # Remove dots and spaces
    rut = rut.replace(".", "").replace(" ", "").strip().upper()
    # If no dash, insert before last char
    if "-" not in rut:
        if len(rut) >= 2:
            rut = rut[:-1] + "-" + rut[-1]
        else:
            return rut
    return rut


def format_rut_for_api(rut: str) -> str:
    """
    Format RUT with dots for ChileCompra API: '12.345.678-9'.
    Accepts normalized form '12345678-9'.
    """
    rut = normalize_rut(rut)
    if not rut or "-" not in rut:
        return rut
    body, dv = rut.rsplit("-", 1)
    # Remove any remaining dots
    body = body.replace(".", "")
    # Add dots every 3 digits from right
    body_with_dots = ""
    for i, ch in enumerate(reversed(body)):
        if i > 0 and i % 3 == 0:
            body_with_dots = "." + body_with_dots
        body_with_dots = ch + body_with_dots
    return f"{body_with_dots}-{dv}"


def validate_rut(rut: str) -> bool:
    """
    Validate Chilean RUT using módulo 11 algorithm.
    Accepts '12345678-9' or '12.345.678-9' formats.
    Returns True if check digit is correct.
    """
    rut = normalize_rut(rut)
    if not rut or "-" not in rut:
        return False
    body, dv = rut.rsplit("-", 1)
    body = body.replace(".", "")
    if not body.isdigit():
        return False
    dv = dv.upper()

    # Compute check digit
    total = 0
    factor = 2
    for ch in reversed(body):
        total += int(ch) * factor
        factor = factor + 1 if factor < 7 else 2

    remainder = total % 11
    computed = 11 - remainder
    if computed == 11:
        computed_dv = "0"
    elif computed == 10:
        computed_dv = "K"
    else:
        computed_dv = str(computed)

    return dv == computed_dv


# ---------------------------------------------------------------------------
# API retry wrapper
# ---------------------------------------------------------------------------

def _is_retryable(exc: BaseException) -> bool:
    """Retry on connection errors and 5xx responses."""
    if isinstance(exc, requests.exceptions.ConnectionError):
        return True
    if isinstance(exc, requests.exceptions.Timeout):
        return True
    if isinstance(exc, requests.exceptions.HTTPError):
        response = getattr(exc, "response", None)
        if response is not None and response.status_code >= 500:
            return True
    return False


@retry(
    retry=retry_if_exception_type((
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    )),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
def _requests_get_with_retry(url: str, **kwargs) -> requests.Response:
    response = requests.get(url, timeout=30, **kwargs)
    if response.status_code >= 500:
        response.raise_for_status()
    return response


def api_get(url: str, params: Optional[Dict[str, Any]] = None, retries: int = 3) -> Dict:
    """
    Retry-wrapped GET request. Returns parsed JSON dict.
    Raises on 4xx (client errors). Retries on 5xx and network errors.

    Args:
        url: Full URL to request
        params: Query parameters dict
        retries: Number of retry attempts (default 3)

    Returns:
        Parsed JSON response as dict
    """
    try:
        response = _requests_get_with_retry(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        logger.error(f"HTTP {status} error for {url}: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        raise


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def iso_week(dt=None) -> str:
    """Return current (or given) ISO week string like '2026-W11'."""
    from datetime import datetime
    if dt is None:
        dt = datetime.utcnow()
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def today_iso() -> str:
    """Return today's date as YYYY-MM-DD."""
    from datetime import date
    return date.today().isoformat()
