"""Transaction cost and capacity models."""

from __future__ import annotations

import numpy as np
import pandas as pd


def flat_bps_cost(turnover: pd.Series, bps: float) -> pd.Series:
    """Flat basis-point cost applied to one-way turnover."""

    return (turnover.fillna(0.0) * bps / 10_000.0).rename("flat_bps_cost")


def spread_proxy_cost(turnover: pd.Series, spread_bps: pd.Series | float) -> pd.Series:
    """Half-spread proxy cost based on one-way turnover."""

    return (turnover.fillna(0.0) * spread_bps / 10_000.0 / 2.0).rename("spread_proxy_cost")


def sqrt_impact_cost(
    weights: pd.DataFrame,
    dollar_volume: pd.DataFrame,
    aum: float,
    impact_coefficient: float = 0.10,
) -> pd.Series:
    """Square-root market-impact proxy.

    Cost is approximated as impact_coefficient * sqrt(dollars_traded / ADV)
    multiplied by traded notional. It returns portfolio return drag.
    """

    trades = weights.fillna(0.0).diff().abs() * aum
    adv = dollar_volume.reindex(index=weights.index, columns=weights.columns).replace(0.0, np.nan)
    participation = trades.div(adv)
    impact_rate = impact_coefficient * np.sqrt(participation.clip(lower=0.0))
    cost_dollars = (trades * impact_rate).sum(axis=1)
    return (cost_dollars / aum).fillna(0.0).rename("sqrt_impact_cost")


def adv_participation(weights: pd.DataFrame, dollar_volume: pd.DataFrame, aum: float) -> pd.DataFrame:
    """Estimate trade participation as dollars traded divided by ADV."""

    trades = weights.fillna(0.0).diff().abs() * aum
    adv = dollar_volume.reindex(index=weights.index, columns=weights.columns).replace(0.0, np.nan)
    return trades.div(adv)


def capacity_table(
    weights: pd.DataFrame,
    dollar_volume: pd.DataFrame,
    gross_returns: pd.Series,
    aum_levels: list[float],
    impact_coefficient: float = 0.10,
) -> pd.DataFrame:
    """Estimate cost-adjusted performance across AUM levels."""

    rows = []
    for aum in aum_levels:
        impact = sqrt_impact_cost(weights, dollar_volume, aum=aum, impact_coefficient=impact_coefficient)
        net = gross_returns.reindex(impact.index).fillna(0.0) - impact
        participation = adv_participation(weights, dollar_volume, aum=aum)
        rows.append(
            {
                "aum": aum,
                "avg_impact_bps": impact.mean() * 10_000,
                "p95_participation": participation.stack(future_stack=True).quantile(0.95),
                "max_participation": participation.stack(future_stack=True).max(),
                "annualized_return_after_impact": net.mean() * 252,
                "annualized_vol_after_impact": net.std(ddof=1) * np.sqrt(252),
                "sharpe_after_impact": np.nan
                if net.std(ddof=1) == 0
                else net.mean() / net.std(ddof=1) * np.sqrt(252),
            }
        )
    return pd.DataFrame(rows)

