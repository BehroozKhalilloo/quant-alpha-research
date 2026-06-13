from __future__ import annotations

import numpy as np

from quant_alpha.backtest import run_long_short_backtest
from quant_alpha.features import build_features
from quant_alpha.portfolio import construct_long_short_weights, sanity_check_weights
from quant_alpha.signal import compute_alpha
from tests.test_features import synthetic_market_data


def test_constructed_weights_are_dollar_neutral_and_capped() -> None:
    data = synthetic_market_data(days=100, tickers=12)
    features = build_features(data, beta_window=10, liquidity_window=10)
    alpha = compute_alpha(features, liquidity_threshold=0.0)
    weights = construct_long_short_weights(alpha["alpha_shifted"], quantiles=4, max_weight=0.50)
    sanity_check_weights(weights, max_weight=0.50)
    assert np.allclose(weights.sum(axis=1), 0.0)
    assert np.allclose(weights.abs().sum(axis=1), 1.0)


def test_backtest_returns_expected_artifacts() -> None:
    data = synthetic_market_data(days=100, tickers=12)
    features = build_features(data, beta_window=10, liquidity_window=10)
    alpha = compute_alpha(features, liquidity_threshold=0.0)
    result = run_long_short_backtest(
        data,
        alpha["alpha_shifted"],
        quantiles=4,
        max_weight=0.50,
        transaction_cost_bps=2.0,
    )
    assert {"weights", "net_returns", "turnover", "summary"}.issubset(result)
    assert result["net_returns"].notna().any()
    assert result["turnover"].ge(0).all()

