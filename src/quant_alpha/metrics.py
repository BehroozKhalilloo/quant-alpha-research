"""Performance and validation metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def annualized_return(returns: pd.Series, periods: int = TRADING_DAYS) -> float:
    """Annualized arithmetic return."""

    return float(returns.dropna().mean() * periods)


def annualized_volatility(returns: pd.Series, periods: int = TRADING_DAYS) -> float:
    """Annualized volatility."""

    return float(returns.dropna().std(ddof=1) * np.sqrt(periods))


def sharpe_ratio(returns: pd.Series, periods: int = TRADING_DAYS) -> float:
    """Annualized Sharpe ratio with zero risk-free rate."""

    vol = returns.dropna().std(ddof=1)
    if vol == 0 or np.isnan(vol):
        return np.nan
    return float(returns.dropna().mean() / vol * np.sqrt(periods))


def sortino_ratio(returns: pd.Series, periods: int = TRADING_DAYS) -> float:
    """Annualized Sortino ratio using downside deviation."""

    clean = returns.dropna()
    downside = clean[clean < 0].std(ddof=1)
    if downside == 0 or np.isnan(downside):
        return np.nan
    return float(clean.mean() / downside * np.sqrt(periods))


def cumulative_returns(returns: pd.Series) -> pd.Series:
    """Compound simple returns."""

    return (1.0 + returns.fillna(0.0)).cumprod() - 1.0


def drawdown(returns: pd.Series) -> pd.Series:
    """Drawdown series from simple returns."""

    equity = (1.0 + returns.fillna(0.0)).cumprod()
    peak = equity.cummax()
    return equity / peak - 1.0


def max_drawdown(returns: pd.Series) -> float:
    """Maximum drawdown."""

    return float(drawdown(returns).min())


def hit_rate(returns: pd.Series) -> float:
    """Fraction of positive return observations."""

    clean = returns.dropna()
    if clean.empty:
        return np.nan
    return float((clean > 0).mean())


def performance_summary(returns: pd.Series) -> pd.Series:
    """Compact summary for a daily return series."""

    return pd.Series(
        {
            "annualized_return": annualized_return(returns),
            "annualized_volatility": annualized_volatility(returns),
            "sharpe_ratio": sharpe_ratio(returns),
            "sortino_ratio": sortino_ratio(returns),
            "max_drawdown": max_drawdown(returns),
            "hit_rate": hit_rate(returns),
        }
    )

