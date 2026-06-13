"""Statistical inference helpers for alpha research."""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.regression.linear_model import OLS
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.sandwich_covariance import cov_hac


def newey_west_mean_test(series: pd.Series, lags: int = 5) -> pd.Series:
    """Autocorrelation-robust t-test for a nonzero mean."""

    clean = series.dropna().astype(float)
    if clean.empty:
        return pd.Series({"mean": np.nan, "nw_t_stat": np.nan, "count": 0})
    x = np.ones((len(clean), 1))
    model = OLS(clean.to_numpy(), x).fit()
    cov = cov_hac(model, nlags=lags)
    se = float(np.sqrt(cov[0, 0]))
    mean = float(model.params[0])
    return pd.Series({"mean": mean, "nw_t_stat": mean / se if se else np.nan, "count": len(clean)})


def false_discovery_report(p_values: pd.Series, alpha: float = 0.10) -> pd.DataFrame:
    """Benjamini-Hochberg false-discovery-aware report."""

    clean = p_values.dropna()
    if clean.empty:
        return pd.DataFrame(columns=["p_value", "bh_reject", "bh_q_value"])
    reject, q_values, _, _ = multipletests(clean.to_numpy(), alpha=alpha, method="fdr_bh")
    return pd.DataFrame({"p_value": clean, "bh_reject": reject, "bh_q_value": q_values}, index=clean.index)

