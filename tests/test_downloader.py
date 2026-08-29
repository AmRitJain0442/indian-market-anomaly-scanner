from dataclasses import replace
from datetime import date

from config import CONFIG
from src.data.nse_downloader import (
    DownloadedSession,
    NSEDownloader,
    bhavcopy_url,
    expected_filename,
)


def test_bhavcopy_url_handles_schema_cutover():
    assert bhavcopy_url(date(2024, 7, 5)).endswith(
        "/2024/JUL/cm05JUL2024bhav.csv.zip"
    )
    assert bhavcopy_url(date(2024, 7, 8)).endswith(
        "/BhavCopy_NSE_CM_0_0_0_20240708_F_0000.csv.zip"
    )
    assert expected_filename(date(2026, 8, 27)).startswith("BhavCopy_NSE_CM")


def test_collect_date_range_uses_exact_weekday_window_and_skips_holidays(tmp_path, monkeypatch):
    config = replace(CONFIG, project_root=tmp_path, artifact_namespace="ten_year")
    downloader = NSEDownloader(config)
    requested = []

    def fake_download(day):
        requested.append(day)
        if day == date(2026, 8, 26):
            return None
        return DownloadedSession(
            day,
            tmp_path / f"{day}.zip",
            "https://example.test",
            "abc",
        )

    monkeypatch.setattr(downloader, "download_one", fake_download)
    sessions = downloader.collect_date_range(date(2026, 8, 24), date(2026, 8, 30))

    assert sorted(requested) == [
        date(2026, 8, 24),
        date(2026, 8, 25),
        date(2026, 8, 26),
        date(2026, 8, 27),
        date(2026, 8, 28),
    ]
    assert [item.session_date for item in sessions] == [
        date(2026, 8, 24),
        date(2026, 8, 25),
        date(2026, 8, 27),
        date(2026, 8, 28),
    ]
    assert (config.raw_dir / "download_manifest_ten_year.json").exists()
