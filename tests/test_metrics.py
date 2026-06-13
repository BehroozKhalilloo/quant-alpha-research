from __future__ import annotations

import numpy as np
import pandas as pd

from quant_alpha.metrics import drawdown, hit_rate, max_drawdown, sharpe_ratio
from quant_alpha.validation import ic_summary, information_coefficient


def test_performance_metrics_are_finite_for_nonconstant_returns() -> None:
    returns = pd.Series([0.01, -0.02, 0.015, 0.003, -0.004])
    assert np.isfinite(sharpe_ratio(returns))
    assert max_drawdown(returns) <= 0
    assert drawdown(returns).iloc[0] == 0
    assert hit_rate(returns) == 0.6


def test_information_coefficient_summary() -> None:
    dates = pd.bdate_range("2024-01-01", periods=5)
    tickers = ["A", "B", "C", "D"]
    index = pd.MultiIndex.from_product([dates, tickers], names=["date", "ticker"])
    signal = pd.Series(np.tile([1.0, 2.0, 3.0, 4.0], len(dates)), index=index)
    target = pd.Series(np.tile([0.01, 0.02, 0.03, 0.04], len(dates)), index=index)
    ic = information_coefficient(signal, target, method="spearman")
    summary = ic_summary(ic)
    assert np.allclose(ic.dropna(), 1.0)
    assert summary["mean"] == 1.0
    assert summary["count"] == 5

