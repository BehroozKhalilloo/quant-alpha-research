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
    base_feature: str = "residual_1d_return",
    direction: str = "reversal",
    vol_adjust: bool = True,
    liquidity_threshold: float = 0.4,
    min_vol: float = 1e-4,
    winsor_lower: float = 0.01,
    winsor_upper: float = 0.99,
    shift_days: int = 1,
) -> pd.DataFrame:
    """Create liquidity-adjusted reversal alpha and its tradable shifted version."""

    required = {base_feature, "realized_vol_21d", "liquidity_rank"}
    missing = required - set(features.columns)
    if missing:
        raise ValueError(f"features missing columns: {sorted(missing)}")

    feature_z = cross_sectional_zscore(features[base_feature])
    if direction == "reversal":
        alpha_raw = -feature_z
    elif direction == "momentum":
        alpha_raw = feature_z
    else:
        raise ValueError("direction must be reversal or momentum")

    vol = features["realized_vol_21d"].clip(lower=min_vol)
    alpha_vol_adj = alpha_raw / vol if vol_adjust else alpha_raw
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


def compute_sleeve(features: pd.DataFrame, sleeve: str) -> pd.Series:
    """Compute a named cross-sectional sleeve before final blending.

    The quality sleeve is a price/volume-based defensive quality proxy because
    the default data source does not include point-in-time fundamentals.
    """

    if sleeve == "reversal_5d":
        return -cross_sectional_zscore(features["return_5d"])
    if sleeve == "residual_reversal_1d":
        return -cross_sectional_zscore(features["residual_1d_return"])
    if sleeve == "momentum_21d":
        return cross_sectional_zscore(features["momentum_21d"])
    if sleeve == "quality_proxy":
        low_vol = -cross_sectional_zscore(features["realized_vol_21d"])
        liquidity = cross_sectional_zscore(features["liquidity_rank"])
        volume_stability = -cross_sectional_zscore((features["volume_shock"] - 1.0).abs())
        return cross_sectional_zscore(0.5 * low_vol + 0.3 * liquidity + 0.2 * volume_stability)
    raise ValueError(f"Unsupported sleeve: {sleeve}")


def compute_blended_alpha(
    features: pd.DataFrame,
    sleeves: dict[str, float],
    winsor_lower: float = 0.01,
    winsor_upper: float = 0.99,
    shift_days: int = 1,
) -> pd.DataFrame:
    """Blend pre-specified sleeve signals into a tradable alpha signal."""

    if not sleeves:
        raise ValueError("sleeves must not be empty")
    weight_sum = sum(abs(weight) for weight in sleeves.values())
    if weight_sum == 0:
        raise ValueError("sleeve weights must not all be zero")

    blended = sum(float(weight) * compute_sleeve(features, sleeve) for sleeve, weight in sleeves.items())
    alpha = cross_sectional_winsorize(blended.replace([np.inf, -np.inf], np.nan), winsor_lower, winsor_upper)
    alpha = cross_sectional_zscore(alpha)
    shifted = alpha.groupby(level="ticker").shift(shift_days)
    out = pd.DataFrame({"alpha": alpha, "alpha_shifted": shifted})
    for sleeve, weight in sleeves.items():
        out[f"sleeve_{sleeve}"] = compute_sleeve(features, sleeve) * float(weight)
    LOGGER.info("Computed blended alpha with shape %s", out.shape)
    return out


def naive_reversal_signal(features: pd.DataFrame, shift_days: int = 1) -> pd.Series:
    """Simple cross-sectional one-day reversal baseline."""

    signal = -cross_sectional_zscore(features["return_1d"])
    return signal.groupby(level="ticker").shift(shift_days).rename("naive_reversal")
