"""Alpha signal construction."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


def cross_sectional_zscore(values: pd.Series) -> pd.Series:
    """Z-score a MultiIndex Series independently for each date."""

    grouped = values.groupby(level="date")
    mean = grouped.transform("mean")
    std = grouped.transform("std").replace(0.0, np.nan)
    return (values - mean) / std


def cross_sectional_winsorize(values: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
    """Winsorize a MultiIndex Series independently for each date."""

    grouped = values.groupby(level="date")
    lo = grouped.transform(lambda x: x.quantile(lower))
    hi = grouped.transform(lambda x: x.quantile(upper))
    return values.clip(lo, hi)


def compute_alpha(
    features: pd.DataFrame,
    liquidity_threshold: float = 0.4,
    min_vol: float = 1e-4,
    winsor_lower: float = 0.01,
    winsor_upper: float = 0.99,
    shift_days: int = 1,
) -> pd.DataFrame:
    """Create liquidity-adjusted reversal alpha and its tradable shifted version."""

    required = {"residual_1d_return", "realized_vol_21d", "liquidity_rank"}
    missing = required - set(features.columns)
    if missing:
        raise ValueError(f"features missing columns: {sorted(missing)}")

    residual_z = cross_sectional_zscore(features["residual_1d_return"])
    alpha_raw = -residual_z
    vol = features["realized_vol_21d"].clip(lower=min_vol)
    alpha_vol_adj = alpha_raw / vol
    liquidity_filter = features["liquidity_rank"] >= liquidity_threshold
    alpha = alpha_vol_adj.where(liquidity_filter)
    alpha = cross_sectional_winsorize(alpha.replace([np.inf, -np.inf], np.nan), winsor_lower, winsor_upper)
    alpha = cross_sectional_zscore(alpha)
    shifted = alpha.groupby(level="ticker").shift(shift_days)

    out = pd.DataFrame(
        {
            "alpha_raw": alpha_raw,
            "alpha_vol_adj": alpha_vol_adj,
            "liquidity_filter": liquidity_filter.astype(float),
            "alpha": alpha,
            "alpha_shifted": shifted,
        }
    )
    LOGGER.info("Computed alpha with shape %s", out.shape)
    return out


def naive_reversal_signal(features: pd.DataFrame, shift_days: int = 1) -> pd.Series:
    """Simple cross-sectional one-day reversal baseline."""

    signal = -cross_sectional_zscore(features["return_1d"])
    return signal.groupby(level="ticker").shift(shift_days).rename("naive_reversal")
