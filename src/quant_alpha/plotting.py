"""Plotting utilities for research reports."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from quant_alpha.metrics import cumulative_returns, drawdown, sharpe_ratio


def _save_or_return(fig: plt.Figure, path: str | Path | None) -> plt.Figure:
    if path is not None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, bbox_inches="tight", dpi=150)
    return fig


def plot_cumulative_returns(returns: pd.Series, path: str | Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4))
    cumulative_returns(returns).plot(ax=ax)
    ax.set_title("Cumulative Long-Short Returns")
    ax.set_ylabel("Cumulative return")
    ax.grid(True, alpha=0.3)
    return _save_or_return(fig, path)


def plot_drawdown(returns: pd.Series, path: str | Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 3))
    drawdown(returns).plot(ax=ax, color="tab:red")
    ax.set_title("Drawdown")
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.3)
    return _save_or_return(fig, path)


def plot_rolling_sharpe(returns: pd.Series, window: int = 63, path: str | Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 3))
    rolling = returns.rolling(window).apply(sharpe_ratio, raw=False)
    rolling.plot(ax=ax)
    ax.set_title(f"Rolling {window}-Day Sharpe")
    ax.grid(True, alpha=0.3)
    return _save_or_return(fig, path)


def plot_ic_time_series(ic: pd.Series, path: str | Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 3))
    ic.plot(ax=ax)
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_title("Information Coefficient")
    ax.grid(True, alpha=0.3)
    return _save_or_return(fig, path)


def plot_ic_by_year(ic_by_year: pd.Series, path: str | Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 3))
    ic_by_year.plot(kind="bar", ax=ax)
    ax.set_title("Rank IC by Year")
    ax.axhline(0.0, color="black", linewidth=1)
    return _save_or_return(fig, path)


def plot_decile_forward_returns(decile_returns: pd.DataFrame, path: str | Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 3))
    decile_returns["mean"].plot(kind="bar", ax=ax)
    ax.set_title("Forward Returns by Signal Decile")
    ax.set_xlabel("Signal decile")
    ax.set_ylabel("Mean forward return")
    ax.axhline(0.0, color="black", linewidth=1)
    return _save_or_return(fig, path)


def plot_turnover(turnover: pd.Series, path: str | Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 3))
    turnover.plot(ax=ax)
    ax.set_title("Portfolio Turnover")
    ax.set_ylabel("One-way turnover")
    ax.grid(True, alpha=0.3)
    return _save_or_return(fig, path)


def plot_beta_exposure(beta_exposure: pd.Series, path: str | Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 3))
    beta_exposure.plot(ax=ax)
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_title("Beta Exposure vs SPY")
    ax.grid(True, alpha=0.3)
    return _save_or_return(fig, path)

