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

