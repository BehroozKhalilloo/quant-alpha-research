"""Statistical validation for cross-sectional alpha signals."""

from __future__ import annotations

import numpy as np
import pandas as pd


def forward_returns(prices: pd.DataFrame, horizon: int = 1) -> pd.Series:
    """Compute forward returns from date t close to date t+h close."""

    close = prices["adj_close"].unstack("ticker").sort_index()
    fwd = close.shift(-horizon).div(close) - 1.0
    out = fwd.stack(future_stack=True).rename(f"forward_return_{horizon}d")
    out.index.names = ["date", "ticker"]
    return out


def information_coefficient(
    signal: pd.Series,
    target: pd.Series,
    method: str = "spearman",
) -> pd.Series:
    """Calculate daily cross-sectional IC."""

    frame = pd.concat({"signal": signal, "target": target}, axis=1).dropna()
    values: dict[pd.Timestamp, float] = {}
    for date, group in frame.groupby(level="date"):
        if group["signal"].nunique() < 2 or group["target"].nunique() < 2:
            values[date] = np.nan
        elif method == "pearson":
            values[date] = group["signal"].corr(group["target"], method="pearson")
        elif method == "spearman":
            values[date] = group["signal"].corr(group["target"], method="spearman")
        else:
            raise ValueError("method must be pearson or spearman")
    return pd.Series(values, name=f"{method}_ic").sort_index()


def ic_summary(ic: pd.Series) -> pd.Series:
    """Return IC mean, standard deviation, and t-statistic."""

    clean = ic.dropna()
    if clean.empty:
        return pd.Series({"mean": np.nan, "std": np.nan, "t_stat": np.nan, "count": 0})
    std = clean.std(ddof=1)
    t_stat = np.nan if std == 0 else clean.mean() / std * np.sqrt(len(clean))
    return pd.Series({"mean": clean.mean(), "std": std, "t_stat": t_stat, "count": len(clean)})


def rank_ic_by_year(signal: pd.Series, target: pd.Series) -> pd.Series:
    """Compute average Spearman rank IC by calendar year."""

    ic = information_coefficient(signal, target, method="spearman")
    return ic.groupby(ic.index.year).mean().rename("rank_ic")


def quantile_forward_returns(
    signal: pd.Series,
    target: pd.Series,
    quantiles: int = 10,
) -> pd.DataFrame:
    """Average forward return by daily signal quantile."""

    frame = pd.concat({"signal": signal, "target": target}, axis=1).dropna()

    def assign_quantile(group: pd.DataFrame) -> pd.Series:
        if group["signal"].nunique() < quantiles:
            return pd.Series(np.nan, index=group.index)
        return pd.qcut(group["signal"], quantiles, labels=False, duplicates="drop") + 1

    frame["quantile"] = frame.groupby(level="date", group_keys=False).apply(assign_quantile)
    return frame.dropna(subset=["quantile"]).groupby("quantile")["target"].agg(["mean", "std", "count"])


def long_short_spread_by_date(signal: pd.Series, target: pd.Series, quantiles: int = 10) -> pd.Series:
    """Top-minus-bottom quantile forward return spread by date."""

    frame = pd.concat({"signal": signal, "target": target}, axis=1).dropna()
    spreads: dict[pd.Timestamp, float] = {}
    for date, group in frame.groupby(level="date"):
        if group["signal"].nunique() < quantiles:
            continue
        labels = pd.qcut(group["signal"], quantiles, labels=False, duplicates="drop") + 1
        group = group.assign(quantile=labels.to_numpy())
        top = group.loc[group["quantile"] == group["quantile"].max(), "target"].mean()
        bottom = group.loc[group["quantile"] == group["quantile"].min(), "target"].mean()
        spreads[date] = top - bottom
    return pd.Series(spreads, name="long_short_forward_spread").sort_index()


def pearson_spearman_summary(signal: pd.Series, target: pd.Series) -> pd.DataFrame:
    """Return IC summaries for Pearson and Spearman methods."""

    rows = {}
    for method in ["pearson", "spearman"]:
        rows[method] = ic_summary(information_coefficient(signal, target, method=method))
    return pd.DataFrame(rows).T
