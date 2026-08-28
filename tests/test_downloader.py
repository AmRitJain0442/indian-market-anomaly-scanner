from datetime import date

from src.data.nse_downloader import bhavcopy_url, expected_filename


def test_bhavcopy_url_handles_schema_cutover():
    assert bhavcopy_url(date(2024, 7, 5)).endswith(
        "/2024/JUL/cm05JUL2024bhav.csv.zip"
    )
    assert bhavcopy_url(date(2024, 7, 8)).endswith(
        "/BhavCopy_NSE_CM_0_0_0_20240708_F_0000.csv.zip"
    )
    assert expected_filename(date(2026, 8, 27)).startswith("BhavCopy_NSE_CM")

