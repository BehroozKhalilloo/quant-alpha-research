from __future__ import annotations

import numpy as np
import pandas as pd

from quant_alpha.features import build_features
from quant_alpha.validation import forward_returns


def synthetic_market_data(days: int = 90, tickers: int = 12) -> pd.DataFrame:
    dates = pd.bdate_range("2024-01-01", periods=days)
    names = ["SPY"] + [f"T{i:02d}" for i in range(tickers - 1)]
    rows = []
    for j, ticker in enumerate(names):
        base = 100 + j
        trend = np.linspace(0, 2 + j * 0.1, days)
        cycle = np.sin(np.arange(days) / (3 + j * 0.1)) * 0.5
        close = base + trend + cycle
        volume = 1_000_000 + j * 50_000 + (np.arange(days) % 7) * 10_000
        frame = pd.DataFrame(
            {
                "date": dates,
                "ticker": ticker,
                "open": close * 0.99,
                "high": close * 1.01,
                "low": close * 0.98,
                "close": close,
                "adj_close": close,
                "volume": volume,
            }
        )
        rows.append(frame)
    return pd.concat(rows).set_index(["date", "ticker"]).sort_index()


def test_build_features_contains_expected_columns() -> None:
    data = synthetic_market_data()
    features = build_features(data, beta_window=10, liquidity_window=10)
    expected = {
        "return_1d",
        "return_5d",
        "momentum_21d",
        "realized_vol_21d",
        "dollar_volume",
        "liquidity_rank",
        "volume_shock",
        "market_beta",
        "residual_1d_return",
    }
    assert expected.issubset(features.columns)
    assert features.index.names == ["date", "ticker"]


def test_forward_returns_uses_future_close_only_for_target() -> None:
    data = synthetic_market_data(days=10, tickers=3)
    target = forward_returns(data, horizon=1)
    close = data["adj_close"].unstack("ticker")
    expected = close.shift(-1).div(close).sub(1).stack(future_stack=True)
    expected.index.names = ["date", "ticker"]
    pd.testing.assert_series_equal(target, expected.rename("forward_return_1d"))
