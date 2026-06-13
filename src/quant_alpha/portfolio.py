"""Portfolio construction and exposure checks."""

from __future__ import annotations

import numpy as np
import pandas as pd


def cap_and_renormalize(weights: pd.Series, max_weight: float) -> pd.Series:
    """Apply position caps and rescale long and short books to 50% gross each."""

    weights = weights.clip(lower=-max_weight, upper=max_weight)
    longs = weights.clip(lower=0.0)
    shorts = weights.clip(upper=0.0)
    if longs.sum() > 0:
        longs = longs / longs.sum() * 0.5
    if shorts.abs().sum() > 0:
        shorts = shorts / shorts.abs().sum() * 0.5
    return longs + shorts


def construct_long_short_weights(
    signal: pd.Series,
    quantiles: int = 10,
    max_weight: float = 0.03,
    weighting: str = "equal",
    vol: pd.Series | None = None,
) -> pd.DataFrame:
    """Long top signal quantile and short bottom signal quantile each day."""

    rows: list[pd.Series] = []
    for date, day_signal in signal.dropna().groupby(level="date"):
        scores = day_signal.droplevel("date")
        if scores.nunique() < quantiles:
            continue
        labels = pd.qcut(scores, quantiles, labels=False, duplicates="drop") + 1
        long_names = labels[labels == labels.max()].index
        short_names = labels[labels == labels.min()].index
        if len(long_names) * max_weight < 0.5 or len(short_names) * max_weight < 0.5:
            continue
        weights = pd.Series(0.0, index=scores.index, name=date)
        if weighting == "equal":
            weights.loc[long_names] = 1.0
            weights.loc[short_names] = -1.0
        elif weighting == "vol_scaled":
            if vol is None:
                raise ValueError("vol must be provided for vol_scaled weighting")
            day_vol = vol.xs(date, level="date").reindex(scores.index).replace(0.0, np.nan)
            inv_vol = 1.0 / day_vol
            weights.loc[long_names] = inv_vol.loc[long_names]
            weights.loc[short_names] = -inv_vol.loc[short_names]
        else:
            raise ValueError("weighting must be equal or vol_scaled")
        weights = cap_and_renormalize(weights, max_weight=max_weight)
        rows.append(weights.rename(date))

    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows).sort_index()
    out.index.name = "date"
    return out


def apply_holding_period(weights: pd.DataFrame, holding_period: int) -> pd.DataFrame:
    """Average overlapping sub-portfolios for multi-day holding periods."""

    if holding_period <= 1 or weights.empty:
        return weights
    held = sum(weights.shift(i).fillna(0.0) for i in range(holding_period)) / holding_period
    return held


def turnover(weights: pd.DataFrame) -> pd.Series:
    """Daily one-way turnover from weight changes."""

    if weights.empty:
        return pd.Series(dtype=float, name="turnover")
    return (weights.fillna(0.0).diff().abs().sum(axis=1) / 2.0).rename("turnover")


def sanity_check_weights(weights: pd.DataFrame, max_weight: float, atol: float = 1e-6) -> None:
    """Validate dollar-neutral long-short portfolio constraints."""

    if weights.empty:
        raise ValueError("weights are empty")
    net = weights.sum(axis=1).abs().dropna()
    gross = weights.abs().sum(axis=1).dropna()
    if (net > atol).any():
        raise ValueError("weights are not dollar neutral")
    if ((gross - 1.0).abs() > 1e-5).any():
        raise ValueError("gross exposure is not approximately one")
    if (weights.abs().max(axis=1) > max_weight + atol).any():
        raise ValueError("position weight exceeds cap")
