from __future__ import annotations

import pandas as pd

from quant_alpha.factor import factor_regression, proxy_factor_returns
from quant_alpha.features import build_features
from quant_alpha.neutralization import build_style_exposures, neutralize_signal
from quant_alpha.trader import almgren_chriss_schedule, kelly_fraction, kelly_scenario_grid
from quant_alpha.validation import evaluate_purged_walk_forward, forward_returns
from tests.test_features import synthetic_market_data


def test_neutralization_reduces_linear_exposure() -> None:
    data = synthetic_market_data(days=90, tickers=8)
    features = build_features(data, beta_window=10, liquidity_window=10)
    exposures = build_style_exposures(features)
    signal = (2.0 * exposures["volatility"] + 0.1).rename("signal")
    neutral = neutralize_signal(signal, exposures, ["volatility"])
    assert neutral.dropna().abs().max() < 1e-10


def test_purged_walk_forward_produces_ordered_folds() -> None:
    data = synthetic_market_data(days=900, tickers=8)
    features = build_features(data, beta_window=10, liquidity_window=10)
    signal = features["return_5d"].groupby(level="ticker").shift(1)
    target = forward_returns(data, horizon=5)
    folds = evaluate_purged_walk_forward(signal, target, train_years=1, test_months=3, embargo_days=5)
    assert not folds.empty
    assert (pd.to_datetime(folds["train_end"]) < pd.to_datetime(folds["test_start"])).all()


def test_factor_regression_and_kelly_outputs() -> None:
    data = synthetic_market_data(days=120, tickers=8)
    factors = proxy_factor_returns(data)
    returns = factors["market_proxy"].fillna(0.0) * 0.2 + 0.001
    regression = factor_regression(returns, factors)
    grid = kelly_scenario_grid(win_probability=0.53, win_loss_ratio=1.1, fractions=[0.25, 0.5])
    assert "coef_market_proxy" in regression.index
    assert kelly_fraction(0.53, 1.1) > 0
    assert len(grid) == 2
    schedule = almgren_chriss_schedule(
        shares=100_000,
        intervals=10,
        volatility=0.02,
        risk_aversion=1e-6,
        temporary_impact=1e-7,
    )
    assert abs(schedule["inventory"].iloc[0] - 100_000) < 1e-6
    assert abs(schedule["inventory"].iloc[-1]) < 1e-6
