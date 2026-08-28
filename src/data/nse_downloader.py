"""Download and cache official NSE cash-market bhavcopies."""

from __future__ import annotations

import hashlib
import json
import logging
import random
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from config import ResearchConfig

LOGGER = logging.getLogger(__name__)
UDIFF_START = date(2024, 7, 8)


class DownloadFailure(RuntimeError):
    """A session could not be classified as available or absent."""


@dataclass(frozen=True)
class DownloadedSession:
    session_date: date
    path: Path
    url: str
    sha256: str


def bhavcopy_url(session_date: date) -> str:
    """Return the official archive URL for either NSE schema generation."""
    if session_date >= UDIFF_START:
        stamp = session_date.strftime("%Y%m%d")
        return (
            "https://nsearchives.nseindia.com/content/cm/"
            f"BhavCopy_NSE_CM_0_0_0_{stamp}_F_0000.csv.zip"
        )
    year = session_date.strftime("%Y")
    month = session_date.strftime("%b").upper()
    stamp = session_date.strftime("%d%b%Y").upper()
    return (
        "https://nsearchives.nseindia.com/content/historical/EQUITIES/"
        f"{year}/{month}/cm{stamp}bhav.csv.zip"
    )


def expected_filename(session_date: date) -> str:
    if session_date >= UDIFF_START:
        return f"BhavCopy_NSE_CM_0_0_0_{session_date:%Y%m%d}_F_0000.csv.zip"
    return f"cm{session_date:%d%b%Y}bhav.csv.zip".upper()


def latest_completed_candidate(now: datetime | None = None) -> date:
    """Return a conservative date from which availability discovery should start."""
    india = ZoneInfo("Asia/Kolkata")
    current = now.astimezone(india) if now else datetime.now(india)
    candidate = current.date()
    # NSE final files are not treated as complete until comfortably after close.
    if current.timetz().replace(tzinfo=None) < dt_time(18, 0):
        candidate -= timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _valid_zip(path: Path) -> bool:
    try:
        return path.stat().st_size > 100 and zipfile.is_zipfile(path)
    except OSError:
        return False


def _candidate_weekdays(end_date: date):
    cursor = end_date
    while True:
        if cursor.weekday() < 5:
            yield cursor
        cursor -= timedelta(days=1)


class NSEDownloader:
    """Rate-limited, retrying downloader with a content-hash manifest."""

    def __init__(self, config: ResearchConfig):
        self.config = config
        self.bhavcopy_dir = config.raw_dir / "bhavcopy"
        self.bhavcopy_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            "User-Agent": config.user_agent,
            "Accept": "application/zip,application/octet-stream,*/*",
        }

    def path_for(self, session_date: date) -> Path:
        return self.bhavcopy_dir / str(session_date.year) / expected_filename(session_date)

    def download_one(self, session_date: date) -> DownloadedSession | None:
        path = self.path_for(session_date)
        url = bhavcopy_url(session_date)
        if _valid_zip(path):
            return DownloadedSession(session_date, path, url, _sha256(path))

        for attempt in range(self.config.request_retries):
            try:
                time.sleep(random.uniform(0.05, 0.20))
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.config.request_timeout_seconds,
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                if not response.content.startswith(b"PK"):
                    raise ValueError("response is not a ZIP archive")
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary = path.with_suffix(path.suffix + ".part")
                temporary.write_bytes(response.content)
                if not _valid_zip(temporary):
                    temporary.unlink(missing_ok=True)
                    raise ValueError("downloaded ZIP failed validation")
                temporary.replace(path)
                return DownloadedSession(session_date, path, url, _sha256(path))
            except (requests.RequestException, OSError, ValueError) as exc:
                if attempt + 1 == self.config.request_retries:
                    raise DownloadFailure(
                        f"Could not classify {session_date} after retries: {exc}"
                    ) from exc
                time.sleep(min(1.0 * (2**attempt), 8.0))
        return None

    def collect_sessions(
        self,
        target: int,
        end_date: date | None = None,
    ) -> list[DownloadedSession]:
        """Download the latest target actual sessions, skipping holidays."""
        if target < 1:
            raise ValueError("target must be positive")
        end = end_date or latest_completed_candidate()
        candidates = _candidate_weekdays(end)
        found: dict[date, DownloadedSession] = {}
        max_candidates = int(target * 1.6) + 60
        checked = 0
        batch_size = max(self.config.download_workers * 3, 18)

        while len(found) < target and checked < max_candidates:
            batch = [next(candidates) for _ in range(batch_size)]
            checked += len(batch)
            with ThreadPoolExecutor(max_workers=self.config.download_workers) as pool:
                futures = {pool.submit(self.download_one, day): day for day in batch}
                for future in as_completed(futures):
                    # A network failure must never be silently interpreted as a holiday.
                    result = future.result()
                    if result is not None:
                        found[result.session_date] = result
            LOGGER.info("Discovered %d/%d sessions", min(len(found), target), target)

        if len(found) < target:
            raise RuntimeError(
                f"Only found {len(found)} NSE sessions after checking {checked} weekdays"
            )

        selected = sorted(found.values(), key=lambda item: item.session_date)[-target:]
        self.write_manifest(selected)
        return selected

    def write_manifest(self, sessions: list[DownloadedSession]) -> Path:
        manifest = {
            "source": "National Stock Exchange of India official archives",
            "generated_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            "sessions": [
                {
                    "date": item.session_date.isoformat(),
                    "file": str(item.path.relative_to(self.config.project_root)),
                    "url": item.url,
                    "sha256": item.sha256,
                }
                for item in sessions
            ],
        }
        path = self.config.raw_dir / "download_manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path
