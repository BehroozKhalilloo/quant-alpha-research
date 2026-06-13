"""Feature engineering for liquidity-adjusted reversal research."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


def _wide(data: pd.DataFrame, column: str) -> pd.DataFrame:
    return data[column].unstack("ticker").sort_index()


def rolling_beta(returns: pd.DataFrame, benchmark: str = "SPY", window: int = 60) -> pd.DataFrame:
    """Estimate rolling beta versus a benchmark using past daily returns."""

    if benchmark not in returns:
        raise ValueError(f"Benchmark {benchmark} must be present in returns")
    market = returns[benchmark]
    covariance = returns.rolling(window).cov(market)
    variance = market.rolling(window).var()
    beta = covariance.div(variance, axis=0)
    return beta.replace([np.inf, -np.inf], np.nan)


def liquidity_percentile(dollar_volume: pd.DataFrame, window: int = 60) -> pd.DataFrame:
    """Compute rolling within-name dollar-volume percentile using only history."""

    return dollar_volume.rolling(window, min_periods=max(10, window // 3)).rank(pct=True)


def build_features(
    market_data: pd.DataFrame,
    benchmark: str = "SPY",
    beta_window: int = 60,
    vol_window: int = 21,
    liquidity_window: int = 60,
    volume_window: int = 20,
) -> pd.DataFrame:
    """Build predictive features from adjusted close and volume.

    Features are known at the close of each date. Backtests must shift signals
    before applying them to later returns.
    """

    missing = {"adj_close", "volume"} - set(market_data.columns)
    if missing:
        raise ValueError(f"market_data missing columns: {sorted(missing)}")

    close = _wide(market_data, "adj_close")
    volume = _wide(market_data, "volume")
    returns = close.pct_change()
    dollar_volume = close * volume
    beta = rolling_beta(returns, benchmark=benchmark, window=beta_window)
    market_return = returns[benchmark]
    residual = returns.sub(beta.mul(market_return, axis=0))

    features = {
        "return_1d": returns,
        "return_5d": close.pct_change(5),
        "momentum_21d": close.pct_change(21),
        "realized_vol_21d": returns.rolling(vol_window).std(),
        "dollar_volume": dollar_volume,
        "liquidity_rank": liquidity_percentile(dollar_volume, liquidity_window),
        "volume_shock": volume.div(volume.rolling(volume_window).mean()),
        "market_beta": beta,
        "residual_1d_return": residual,
    }

    long_frames = []
    for name, frame in features.items():
        stacked = frame.stack(future_stack=True).rename(name)
        long_frames.append(stacked)

    out = pd.concat(long_frames, axis=1)
    out.index.names = ["date", "ticker"]
    LOGGER.info("Built features with shape %s", out.shape)
    return out.sort_index()


def add_sector_neutral_zscore(
    alpha: pd.Series,
    sector_map: dict[str, str],
) -> pd.Series:
    """Compute date-level sector-neutral z-scores when sector metadata exists."""

    frame = alpha.rename("alpha").reset_index()
    frame["sector"] = frame["ticker"].map(sector_map)
    grouped = frame.groupby(["date", "sector"], dropna=True)["alpha"]
    mean = grouped.transform("mean")
    std = grouped.transform("std").replace(0.0, np.nan)
    frame["sector_neutral_alpha"] = (frame["alpha"] - mean) / std
    return frame.set_index(["date", "ticker"])["sector_neutral_alpha"].sort_index()
