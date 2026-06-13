"""Advanced diagnostics for alpha research reports."""

from __future__ import annotations

import numpy as np
import pandas as pd

from quant_alpha.metrics import max_drawdown, performance_summary, sharpe_ratio


def block_bootstrap_summary(
    returns: pd.Series,
    n_bootstrap: int = 1000,
    block_size: int = 21,
    seed: int = 42,
) -> pd.DataFrame:
    """Estimate confidence intervals for annualized return, Sharpe, and drawdown.

    A moving-block bootstrap preserves short-run autocorrelation better than
    independently resampling daily returns.
    """

    clean = returns.dropna()
    if clean.empty:
        return pd.DataFrame()
    rng = np.random.default_rng(seed)
    values = clean.to_numpy()
    n_obs = len(values)
    rows = []
    for _ in range(n_bootstrap):
        sampled: list[float] = []
        while len(sampled) < n_obs:
            start = int(rng.integers(0, max(1, n_obs - block_size + 1)))
            sampled.extend(values[start : start + block_size])
        sample = pd.Series(sampled[:n_obs], index=clean.index)
        rows.append(
            {
                "annualized_return": performance_summary(sample)["annualized_return"],
                "sharpe_ratio": sharpe_ratio(sample),
                "max_drawdown": max_drawdown(sample),
            }
        )
    sims = pd.DataFrame(rows)
    return pd.DataFrame(
        {
            "p05": sims.quantile(0.05),
            "median": sims.quantile(0.50),
            "p95": sims.quantile(0.95),
        }
    )


def rolling_performance(returns: pd.Series, window: int = 126) -> pd.DataFrame:
    """Rolling annualized return, volatility, Sharpe, and max drawdown."""

    clean = returns.dropna()
    out = pd.DataFrame(index=clean.index)
    out["rolling_ann_return"] = clean.rolling(window).mean() * 252
    out["rolling_ann_vol"] = clean.rolling(window).std(ddof=1) * np.sqrt(252)
    out["rolling_sharpe"] = clean.rolling(window).apply(sharpe_ratio, raw=False)
    out["rolling_max_drawdown"] = clean.rolling(window).apply(max_drawdown, raw=False)
    return out.dropna(how="all")


def monthly_return_table(returns: pd.Series) -> pd.DataFrame:
    """Monthly compounded returns indexed by year and month."""

    clean = returns.dropna()
    monthly = (1.0 + clean).resample("ME").prod() - 1.0
    table = monthly.to_frame("return")
    table["year"] = table.index.year
    table["month"] = table.index.month
    return table.pivot(index="year", columns="month", values="return")


def regime_summary(strategy_returns: pd.Series, benchmark_returns: pd.Series) -> pd.DataFrame:
    """Summarize strategy performance by simple benchmark regimes."""

    frame = pd.concat({"strategy": strategy_returns, "benchmark": benchmark_returns}, axis=1).dropna()
    if frame.empty:
        return pd.DataFrame()
    benchmark_trend = (1.0 + frame["benchmark"]).rolling(21).apply(np.prod, raw=True) - 1.0
    realized_vol = frame["benchmark"].rolling(21).std()
    vol_cut = realized_vol.median()
    frame["market_regime"] = np.where(benchmark_trend >= 0, "positive_21d_trend", "negative_21d_trend")
    frame["vol_regime"] = np.where(realized_vol <= vol_cut, "low_vol", "high_vol")
    rows = []
    for group_name in ["market_regime", "vol_regime"]:
        for regime, group in frame.groupby(group_name):
            summary = performance_summary(group["strategy"])
            rows.append(
                {
                    "group": group_name,
                    "regime": regime,
                    "count": len(group),
                    **summary.to_dict(),
                }
            )
    return pd.DataFrame(rows)


def drawdown_events(returns: pd.Series, top_n: int = 5) -> pd.DataFrame:
    """Identify the largest drawdown episodes."""

    clean = returns.dropna()
    equity = (1.0 + clean).cumprod()
    peak = equity.cummax()
    dd = equity / peak - 1.0
    events = []
    in_drawdown = False
    start = trough = None
    trough_value = 0.0
    for date, value in dd.items():
        if value < 0 and not in_drawdown:
            in_drawdown = True
            start = date
            trough = date
            trough_value = value
        elif value < 0 and in_drawdown:
            if value < trough_value:
                trough = date
                trough_value = value
        elif value == 0 and in_drawdown:
            events.append(
                {
                    "start": start,
                    "trough": trough,
                    "recovery": date,
                    "max_drawdown": trough_value,
                    "days_to_trough": (trough - start).days,
                    "days_to_recovery": (date - start).days,
                }
            )
            in_drawdown = False
    if in_drawdown:
        events.append(
            {
                "start": start,
                "trough": trough,
                "recovery": pd.NaT,
                "max_drawdown": trough_value,
                "days_to_trough": (trough - start).days,
                "days_to_recovery": np.nan,
            }
        )
    return pd.DataFrame(events).sort_values("max_drawdown").head(top_n)
