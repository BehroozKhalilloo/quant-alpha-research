"""Data quality and point-in-time universe helpers."""

from __future__ import annotations

import pandas as pd


def validate_market_data(
    market_data: pd.DataFrame,
    stale_window: int = 5,
    extreme_return: float = 0.35,
) -> dict[str, pd.DataFrame]:
    """Run lightweight data quality checks on long-form OHLCV data.

    These checks are intentionally vendor-agnostic. They flag suspicious rows;
    they do not attempt to repair prices because corporate-action treatment is
    provider-specific.
    """

    required = {"open", "high", "low", "close", "adj_close", "volume"}
    missing_cols = required - set(market_data.columns)
    if missing_cols:
        raise ValueError(f"market_data missing columns: {sorted(missing_cols)}")

    data = market_data.sort_index()
    close = data["adj_close"].unstack("ticker")
    volume = data["volume"].unstack("ticker")
    returns = close.pct_change()

    reports: dict[str, pd.DataFrame] = {}
    reports["missing_by_ticker"] = data[list(required)].isna().groupby("ticker").sum()
    reports["nonpositive_prices"] = data.loc[
        (data[["open", "high", "low", "close", "adj_close"]] <= 0).any(axis=1),
        ["open", "high", "low", "close", "adj_close"],
    ]
    reports["negative_volume"] = data.loc[data["volume"] < 0, ["volume"]]

    stale = close.pct_change().abs().rolling(stale_window).sum() == 0
    reports["stale_prices"] = stale.stack(future_stack=True).rename("is_stale").to_frame().query("is_stale")

    extreme = returns.abs() > extreme_return
    reports["extreme_returns"] = (
        returns.where(extreme)
        .stack(future_stack=True)
        .rename("return")
        .dropna()
        .sort_values(key=lambda s: s.abs(), ascending=False)
        .to_frame()
    )

    zero_volume = volume <= 0
    reports["zero_volume"] = zero_volume.stack(future_stack=True).rename("zero_volume").to_frame().query("zero_volume")

    coverage = close.notna().mean(axis=1).rename("coverage").to_frame()
    reports["daily_coverage"] = coverage
    return reports


def summarize_quality_report(reports: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Summarize data quality report sizes for easy reporting."""

    rows = []
    for name, frame in reports.items():
        rows.append({"check": name, "rows_flagged": len(frame), "columns": ",".join(map(str, frame.columns))})
    return pd.DataFrame(rows)


def load_universe_membership(path: str) -> pd.DataFrame:
    """Load optional point-in-time universe membership.

    Expected columns: date, ticker, in_universe. The file can be supplied by a
    user with CRSP/Norgate/FactSet-like membership data. yfinance cannot provide
    this information.
    """

    membership = pd.read_csv(path, parse_dates=["date"])
    required = {"date", "ticker", "in_universe"}
    missing = required - set(membership.columns)
    if missing:
        raise ValueError(f"Universe membership file missing columns: {sorted(missing)}")
    return membership.sort_values(["date", "ticker"])


def apply_point_in_time_universe(signal: pd.Series, membership: pd.DataFrame) -> pd.Series:
    """Mask a MultiIndex signal with point-in-time universe membership."""

    member = membership.set_index(["date", "ticker"])["in_universe"].astype(bool)
    aligned = member.reindex(signal.index).fillna(False)
    return signal.where(aligned)

