from __future__ import annotations

import numpy as np
import pandas as pd

from quant_alpha.features import build_features
from quant_alpha.signal import compute_alpha, compute_blended_alpha, cross_sectional_zscore
from tests.test_features import synthetic_market_data


def test_cross_sectional_zscore_has_daily_zero_mean() -> None:
    dates = pd.bdate_range("2024-01-01", periods=3)
    index = pd.MultiIndex.from_product([dates, ["A", "B", "C"]], names=["date", "ticker"])
    values = pd.Series(np.arange(len(index), dtype=float), index=index)
    z = cross_sectional_zscore(values)
    means = z.groupby(level="date").mean().round(12)
    assert (means == 0).all()


def test_alpha_is_shifted_by_ticker() -> None:
    data = synthetic_market_data()
    features = build_features(data, beta_window=10, liquidity_window=10)
    alpha = compute_alpha(features, liquidity_threshold=0.0)
    ticker = "T01"
    raw = alpha["alpha"].xs(ticker, level="ticker")
    shifted = alpha["alpha_shifted"].xs(ticker, level="ticker")
    pd.testing.assert_series_equal(shifted, raw.shift(1), check_names=False)


def test_blended_alpha_contains_weighted_sleeves_and_shift() -> None:
    data = synthetic_market_data()
    features = build_features(data, beta_window=10, liquidity_window=10)
    alpha = compute_blended_alpha(
        features,
        sleeves={
            "reversal_5d": 0.8,
            "residual_reversal_1d": 0.1,
            "momentum_21d": 0.05,
            "quality_proxy": 0.05,
        },
    )
    assert "alpha_shifted" in alpha
    assert "sleeve_reversal_5d" in alpha
    ticker = "T01"
    raw = alpha["alpha"].xs(ticker, level="ticker")
    shifted = alpha["alpha_shifted"].xs(ticker, level="ticker")
    pd.testing.assert_series_equal(shifted, raw.shift(1), check_names=False)
