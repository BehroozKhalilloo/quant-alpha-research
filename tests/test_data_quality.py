from __future__ import annotations

from quant_alpha.data_quality import summarize_quality_report, validate_market_data
from tests.test_features import synthetic_market_data


def test_validate_market_data_flags_quality_checks() -> None:
    data = synthetic_market_data(days=30, tickers=4)
    reports = validate_market_data(data, stale_window=3, extreme_return=0.2)
    summary = summarize_quality_report(reports)
    assert {"missing_by_ticker", "daily_coverage"}.issubset(reports)
    assert {"check", "rows_flagged"}.issubset(summary.columns)


def test_validate_market_data_detects_nonpositive_price() -> None:
    data = synthetic_market_data(days=30, tickers=4).copy()
    idx = data.index[0]
    data.loc[idx, "adj_close"] = 0.0
    reports = validate_market_data(data)
    assert not reports["nonpositive_prices"].empty

