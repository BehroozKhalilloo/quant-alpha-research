"""Factor attribution helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm


def load_factor_returns(path: str) -> pd.DataFrame:
    """Load user-supplied factor returns indexed by date."""

    factors = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    return factors.apply(pd.to_numeric, errors="coerce")


def factor_regression(returns: pd.Series, factors: pd.DataFrame, lags: int = 5) -> pd.Series:
    """Run HAC-robust factor regression for strategy returns."""

    frame = pd.concat([returns.rename("strategy"), factors], axis=1).dropna()
    if len(frame) <= factors.shape[1] + 5:
        return pd.Series(dtype=float)
    y = frame["strategy"]
    x = sm.add_constant(frame.drop(columns=["strategy"]))
    model = sm.OLS(y, x).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    out = pd.Series(model.params, index=[f"coef_{name}" for name in model.params.index])
    for name, value in model.tvalues.items():
        out[f"t_{name}"] = value
    out["r_squared"] = model.rsquared
    out["n_obs"] = len(frame)
    return out


def proxy_factor_returns(market_data: pd.DataFrame, benchmark: str = "SPY") -> pd.DataFrame:
    """Build a minimal public-data factor proxy panel.

    This is not a replacement for Fama-French or q-factor data. It provides a
    market proxy so the report can distinguish raw performance from market beta.
    """

    close = market_data["adj_close"].unstack("ticker").sort_index()
    returns = close.pct_change()
    if benchmark not in returns:
        raise ValueError(f"{benchmark} not found in market data")
    factors = pd.DataFrame(index=returns.index)
    factors["market_proxy"] = returns[benchmark]
    mega_cols = [col for col in ["AAPL", "MSFT", "NVDA", "AMZN", "META"] if col in returns]
    non_benchmark = returns.drop(columns=[benchmark], errors="ignore")
    factors["mega_cap_proxy"] = returns[mega_cols].mean(axis=1) if mega_cols else non_benchmark.mean(axis=1)
    factors["cross_sectional_dispersion"] = non_benchmark.std(axis=1)
    return factors.replace([np.inf, -np.inf], np.nan)
