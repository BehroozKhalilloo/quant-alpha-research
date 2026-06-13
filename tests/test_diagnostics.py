from __future__ import annotations

import numpy as np
import pandas as pd

from quant_alpha.diagnostics import (
    block_bootstrap_summary,
    drawdown_events,
    monthly_return_table,
    regime_summary,
    rolling_performance,
)


def test_block_bootstrap_summary_returns_expected_rows() -> None:
    returns = pd.Series([0.01, -0.005, 0.002, 0.004] * 20, index=pd.bdate_range("2024-01-01", periods=80))
    summary = block_bootstrap_summary(returns, n_bootstrap=20, block_size=5, seed=1)
    assert {"annualized_return", "sharpe_ratio", "max_drawdown"}.issubset(summary.index)
    assert {"p05", "median", "p95"}.issubset(summary.columns)


def test_rolling_monthly_regime_and_drawdowns() -> None:
    dates = pd.bdate_range("2024-01-01", periods=160)
    strategy = pd.Series(np.sin(np.arange(160) / 9) / 100, index=dates)
    benchmark = pd.Series(np.cos(np.arange(160) / 11) / 120, index=dates)
    rolling = rolling_performance(strategy, window=21)
    monthly = monthly_return_table(strategy)
    regimes = regime_summary(strategy, benchmark)
    drawdowns = drawdown_events(strategy, top_n=3)
    assert not rolling.empty
    assert not monthly.empty
    assert {"group", "regime", "sharpe_ratio"}.issubset(regimes.columns)
    assert len(drawdowns) <= 3

