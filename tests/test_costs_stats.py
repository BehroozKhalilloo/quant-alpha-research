from __future__ import annotations

import numpy as np
import pandas as pd

from quant_alpha.costs import capacity_table, flat_bps_cost, sqrt_impact_cost
from quant_alpha.stats import false_discovery_report, newey_west_mean_test


def test_cost_models_return_nonnegative_costs() -> None:
    dates = pd.bdate_range("2024-01-01", periods=5)
    weights = pd.DataFrame({"A": [0.0, 0.5, 0.4, 0.2, 0.0], "B": [0.0, -0.5, -0.4, -0.2, 0.0]}, index=dates)
    dollar_volume = pd.DataFrame(10_000_000.0, index=dates, columns=["A", "B"])
    turnover = weights.diff().abs().sum(axis=1) / 2.0
    assert flat_bps_cost(turnover, 5.0).ge(0).all()
    assert sqrt_impact_cost(weights, dollar_volume, aum=1_000_000).ge(0).all()
    capacity = capacity_table(weights, dollar_volume, pd.Series(0.001, index=dates), [1_000_000])
    assert capacity.loc[0, "aum"] == 1_000_000


def test_newey_west_and_fdr_outputs() -> None:
    series = pd.Series(np.linspace(-0.01, 0.02, 40))
    nw = newey_west_mean_test(series, lags=3)
    fdr = false_discovery_report(pd.Series({"a": 0.01, "b": 0.20}))
    assert {"mean", "nw_t_stat", "count"}.issubset(nw.index)
    assert {"p_value", "bh_reject", "bh_q_value"}.issubset(fdr.columns)

