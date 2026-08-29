from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd

from config import CONFIG
from src.data.bhavcopy_parser import parse_bhavcopy, validate_market_data


def test_legacy_parser_filters_to_ordinary_equities(tmp_path):
    rows = pd.DataFrame(
        [
            {
                "SYMBOL": "ORDINARY",
                "SERIES": "EQ",
                "OPEN": 100,
                "HIGH": 110,
                "LOW": 99,
                "CLOSE": 108,
                "LAST": 108,
                "PREVCLOSE": 100,
                "TOTTRDQTY": 1000,
                "TOTTRDVAL": 105000,
                "TIMESTAMP": "05-JUL-2024",
                "TOTALTRADES": 50,
                "ISIN": "INE000000001",
            },
            {
                "SYMBOL": "ETF",
                "SERIES": "EQ",
                "OPEN": 10,
                "HIGH": 10,
                "LOW": 10,
                "CLOSE": 10,
                "LAST": 10,
                "PREVCLOSE": 10,
                "TOTTRDQTY": 100,
                "TOTTRDVAL": 1000,
                "TIMESTAMP": "05-JUL-2024",
                "TOTALTRADES": 5,
                "ISIN": "INF000000001",
            },
            {
                "SYMBOL": "ISSUER-RE1",
                "SERIES": "EQ",
                "OPEN": 5,
                "HIGH": 6,
                "LOW": 4,
                "CLOSE": 5,
                "LAST": 5,
                "PREVCLOSE": 5,
                "TOTTRDQTY": 500,
                "TOTTRDVAL": 2500,
                "TIMESTAMP": "05-JUL-2024",
                "TOTALTRADES": 10,
                "ISIN": "INE000000002",
            },
        ]
    )
    csv_path = tmp_path / "sample.csv"
    rows.to_csv(csv_path, index=False)
    zip_path = tmp_path / "sample.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        archive.write(csv_path, arcname="sample.csv")
    parsed = parse_bhavcopy(zip_path, CONFIG)
    assert parsed["symbol"].tolist() == ["ORDINARY"]
    assert parsed.iloc[0]["traded_value"] == 105000


def test_validation_flags_extreme_return_without_deleting_it():
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-02"]),
            "symbol": ["SPLIT"],
            "isin": ["INE000000001"],
            "company_name": ["Split Ltd"],
            "series": ["EQ"],
            "open": [50.0],
            "high": [51.0],
            "low": [49.0],
            "close": [50.0],
            "last_price": [50.0],
            "previous_close": [100.0],
            "volume": [1000],
            "traded_value": [50000],
            "number_of_trades": [20],
            "delivery_quantity": [None],
            "delivery_percentage": [None],
            "instrument_type": ["STK"],
        }
    )
    validated, report = validate_market_data(frame)
    assert len(validated) == 1
    assert bool(validated.iloc[0]["corporate_action_flag"])
    assert report["extreme_discontinuity_rows"] == 1


def test_legacy_parser_accepts_two_digit_year_used_by_nse_archive(tmp_path):
    row = pd.DataFrame(
        [
            {
                "SYMBOL": "ARCHIVE",
                "SERIES": "EQ",
                "OPEN": 100,
                "HIGH": 102,
                "LOW": 99,
                "CLOSE": 101,
                "LAST": 101,
                "PREVCLOSE": 100,
                "TOTTRDQTY": 1000,
                "TOTTRDVAL": 101000,
                "TIMESTAMP": "13-Jul-20",
                "TOTALTRADES": 50,
                "ISIN": "INE000000099",
            }
        ]
    )
    csv_path = tmp_path / "legacy.csv"
    row.to_csv(csv_path, index=False)
    zip_path = tmp_path / "legacy.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        archive.write(csv_path, arcname="legacy.csv")

    parsed = parse_bhavcopy(zip_path, CONFIG)

    assert parsed.iloc[0]["date"] == pd.Timestamp("2020-07-13")
