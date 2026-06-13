"""Vectorized daily long-short backtest."""

from __future__ import annotations

import logging

import pandas as pd

from quant_alpha.metrics import performance_summary
from quant_alpha.portfolio import apply_holding_period, construct_long_short_weights, sanity_check_weights, turnover

LOGGER = logging.getLogger(__name__)


def daily_returns(market_data: pd.DataFrame) -> pd.DataFrame:
    """Wide daily adjusted-close returns."""

    close = market_data["adj_close"].unstack("ticker").sort_index()
    return close.pct_change()


def run_long_short_backtest(
    market_data: pd.DataFrame,
    signal: pd.Series,
    quantiles: int = 10,
    transaction_cost_bps: float = 5.0,
    max_weight: float = 0.03,
    holding_period: int = 1,
    weighting: str = "equal",
    vol: pd.Series | None = None,
) -> dict[str, pd.DataFrame | pd.Series]:
    """Run a vectorized close-to-close long-short backtest.

    Weights formed from signal timestamp t are applied to t+1 close-to-close
    returns by shifting weights one row forward.
    """

    returns = daily_returns(market_data)
    weights = construct_long_short_weights(
        signal=signal,
        quantiles=quantiles,
        max_weight=max_weight,
        weighting=weighting,
        vol=vol,
    )
    weights = apply_holding_period(weights, holding_period=holding_period)
    if weights.empty:
        raise ValueError("No portfolio weights constructed")
    weights = weights.loc[weights.abs().sum(axis=1) > 0.99]
    sanity_check_weights(weights.dropna(how="all"), max_weight=max_weight)

    aligned_returns = returns.reindex(index=weights.index, columns=weights.columns)
    execution_weights = weights.shift(1).reindex_like(aligned_returns).fillna(0.0)
    gross_returns = (execution_weights * aligned_returns).sum(axis=1).rename("gross_return")
    daily_turnover = turnover(weights).reindex(gross_returns.index).fillna(0.0)
    costs = (transaction_cost_bps / 10_000.0 * daily_turnover).rename("transaction_cost")
    net_returns = (gross_returns - costs).rename("net_return")

    LOGGER.info("Backtest produced %d daily returns", len(net_returns.dropna()))
    return {
        "weights": weights,
        "execution_weights": execution_weights,
        "gross_returns": gross_returns,
        "net_returns": net_returns,
        "turnover": daily_turnover,
        "transaction_costs": costs,
        "summary": performance_summary(net_returns),
    }


def benchmark_returns(market_data: pd.DataFrame, benchmark: str = "SPY") -> pd.Series:
    """Adjusted-close returns for the benchmark ticker."""

    returns = daily_returns(market_data)
    if benchmark not in returns:
        raise ValueError(f"Benchmark {benchmark} not present in data")
    return returns[benchmark].rename(f"{benchmark}_return")
