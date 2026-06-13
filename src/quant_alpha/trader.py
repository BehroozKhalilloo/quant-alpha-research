"""Trader-facing Kelly sizing and risk-of-ruin utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def kelly_fraction(win_probability: float, win_loss_ratio: float) -> float:
    """Full Kelly fraction for a binary payoff."""

    if not 0 <= win_probability <= 1:
        raise ValueError("win_probability must be between 0 and 1")
    if win_loss_ratio <= 0:
        raise ValueError("win_loss_ratio must be positive")
    q = 1.0 - win_probability
    return win_probability - q / win_loss_ratio


def simulate_fractional_kelly(
    win_probability: float,
    win_loss_ratio: float,
    fraction: float,
    n_bets: int = 252,
    n_paths: int = 5000,
    seed: int = 42,
) -> pd.DataFrame:
    """Simulate wealth paths for fractional Kelly sizing."""

    full_kelly = kelly_fraction(win_probability, win_loss_ratio)
    bet_fraction = fraction * full_kelly
    rng = np.random.default_rng(seed)
    wins = rng.random((n_paths, n_bets)) < win_probability
    returns = np.where(wins, bet_fraction * win_loss_ratio, -bet_fraction)
    wealth = np.cumprod(1.0 + returns, axis=1)
    terminal = wealth[:, -1]
    max_drawdown = np.min(wealth / np.maximum.accumulate(wealth, axis=1) - 1.0, axis=1)
    return pd.DataFrame(
        {
            "fractional_kelly": fraction,
            "full_kelly": full_kelly,
            "bet_fraction": bet_fraction,
            "terminal_wealth_p05": np.quantile(terminal, 0.05),
            "terminal_wealth_median": np.quantile(terminal, 0.50),
            "terminal_wealth_p95": np.quantile(terminal, 0.95),
            "probability_loss": np.mean(terminal < 1.0),
            "median_max_drawdown": np.median(max_drawdown),
            "p05_max_drawdown": np.quantile(max_drawdown, 0.05),
        },
        index=[0],
    )


def kelly_scenario_grid(
    win_probability: float = 0.525,
    win_loss_ratio: float = 1.05,
    fractions: list[float] | None = None,
) -> pd.DataFrame:
    """Run scenario analysis for common fractional Kelly levels."""

    fractions = fractions or [0.0, 0.25, 0.50, 0.75, 1.0]
    return pd.concat(
        [simulate_fractional_kelly(win_probability, win_loss_ratio, fraction) for fraction in fractions],
        ignore_index=True,
    )


def almgren_chriss_schedule(
    shares: float,
    intervals: int,
    volatility: float,
    risk_aversion: float,
    temporary_impact: float,
    permanent_impact: float = 0.0,
) -> pd.DataFrame:
    """Compute a simple Almgren-Chriss liquidation schedule.

    The implementation uses the standard hyperbolic trajectory for temporary
    impact and inventory risk. Units are abstract and intended for scenario
    analysis, not production execution.
    """

    if intervals <= 0:
        raise ValueError("intervals must be positive")
    if shares <= 0 or volatility < 0 or risk_aversion < 0 or temporary_impact <= 0:
        raise ValueError("invalid Almgren-Chriss parameters")
    times = np.arange(intervals + 1)
    if risk_aversion == 0 or volatility == 0:
        inventory = shares * (1.0 - times / intervals)
    else:
        kappa = np.sqrt(risk_aversion * volatility**2 / temporary_impact)
        grid = intervals - times
        inventory = shares * np.sinh(kappa * grid) / np.sinh(kappa * intervals)
    trades = -np.diff(inventory, prepend=shares)
    trades[0] = 0.0
    temporary_cost = temporary_impact * trades**2
    permanent_cost = permanent_impact * trades * np.maximum(inventory, 0.0)
    risk_penalty = risk_aversion * volatility**2 * inventory**2
    return pd.DataFrame(
        {
            "interval": times,
            "inventory": inventory,
            "trade": trades,
            "temporary_cost": temporary_cost,
            "permanent_cost": permanent_cost,
            "risk_penalty": risk_penalty,
            "total_objective_cost": temporary_cost + permanent_cost + risk_penalty,
        }
    )
