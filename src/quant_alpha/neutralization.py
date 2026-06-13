"""Cross-sectional signal neutralization utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _residualize(y: pd.Series, x: pd.DataFrame) -> pd.Series:
    frame = pd.concat([y.rename("y"), x], axis=1).replace([np.inf, -np.inf], np.nan).dropna()
    out = pd.Series(np.nan, index=y.index)
    if len(frame) <= x.shape[1] + 2:
        return out
    design = np.column_stack([np.ones(len(frame)), frame[x.columns].to_numpy(dtype=float)])
    beta, *_ = np.linalg.lstsq(design, frame["y"].to_numpy(dtype=float), rcond=None)
    fitted = design @ beta
    out.loc[frame.index] = frame["y"] - fitted
    return out


def neutralize_signal(
    signal: pd.Series,
    exposures: pd.DataFrame,
    exposure_columns: list[str],
) -> pd.Series:
    """Residualize a MultiIndex signal against cross-sectional exposures by date."""

    missing = set(exposure_columns) - set(exposures.columns)
    if missing:
        raise ValueError(f"Missing exposure columns: {sorted(missing)}")
    aligned = exposures[exposure_columns].reindex(signal.index)
    pieces = []
    for date, day_signal in signal.groupby(level="date"):
        day_x = aligned.xs(date, level="date")
        residual = _residualize(day_signal.droplevel("date"), day_x)
        residual.index = pd.MultiIndex.from_product([[date], residual.index], names=["date", "ticker"])
        pieces.append(residual)
    if not pieces:
        return signal.copy() * np.nan
    return pd.concat(pieces).sort_index().rename(signal.name)


def build_style_exposures(features: pd.DataFrame) -> pd.DataFrame:
    """Construct beta, size, volatility, momentum, and liquidity style exposures."""

    out = pd.DataFrame(index=features.index)
    out["beta"] = features["market_beta"]
    out["size_proxy"] = np.log(features["dollar_volume"].replace(0.0, np.nan))
    out["volatility"] = features["realized_vol_21d"]
    out["momentum"] = features["momentum_21d"]
    out["liquidity"] = features["liquidity_rank"]
    return out

