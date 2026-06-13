#!/usr/bin/env python
"""Run robustness checks for candidate alpha specifications."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd

from quant_alpha.backtest import run_long_short_backtest
from quant_alpha.data import load_market_data
from quant_alpha.features import build_features
from quant_alpha.signal import compute_alpha, compute_blended_alpha
from quant_alpha.utils import ensure_dir, load_config, setup_logging
from quant_alpha.validation import forward_returns, information_coefficient


def exclude_ticker(series: pd.Series, ticker: str) -> pd.Series:
    """Remove a ticker from a MultiIndex Series."""

    return series[series.index.get_level_values("ticker") != ticker]


def ic_stats(ic: pd.Series) -> dict[str, float]:
    """Return mean, standard deviation, t-statistic, and count for an IC series."""

    clean = ic.dropna()
    if clean.empty:
        return {"mean": np.nan, "std": np.nan, "t_stat": np.nan, "count": 0}
    std = clean.std(ddof=1)
    t_stat = np.nan if std == 0 else clean.mean() / std * np.sqrt(len(clean))
    return {"mean": clean.mean(), "std": std, "t_stat": t_stat, "count": len(clean)}


def evaluate_candidate(
    name: str,
    market_data: pd.DataFrame,
    features: pd.DataFrame,
    benchmark: str,
    split_date: str,
    quantiles: int,
    max_weight: float,
    transaction_cost_bps: float,
    base_feature: str,
    direction: str,
    vol_adjust: bool,
    liquidity_threshold: float,
    horizon: int,
    holding_period: int,
    sleeves: dict[str, float] | None = None,
) -> dict[str, float | str]:
    """Evaluate a single signal candidate with split IC and backtest metrics."""

    if sleeves:
        alpha = compute_blended_alpha(features, sleeves=sleeves)
    else:
        alpha = compute_alpha(
            features,
            base_feature=base_feature,
            direction=direction,
            vol_adjust=vol_adjust,
            liquidity_threshold=liquidity_threshold,
        )
    signal = exclude_ticker(alpha["alpha_shifted"], benchmark)
    target = exclude_ticker(forward_returns(market_data, horizon=horizon), benchmark)
    ic = information_coefficient(signal, target, method="spearman")
    split = pd.Timestamp(split_date)
    train = ic[ic.index < split]
    test = ic[ic.index >= split]
    bt = run_long_short_backtest(
        market_data=market_data,
        signal=signal,
        quantiles=quantiles,
        transaction_cost_bps=transaction_cost_bps,
        max_weight=max_weight,
        holding_period=holding_period,
    )

    train_stats = ic_stats(train)
    test_stats = ic_stats(test)
    summary = bt["summary"]
    return {
        "candidate": name,
        "base_feature": base_feature,
        "direction": direction,
        "vol_adjust": vol_adjust,
        "liquidity_threshold": liquidity_threshold,
        "horizon": horizon,
        "holding_period": holding_period,
        "sleeves": str(sleeves) if sleeves else "",
        "train_rank_ic": train_stats["mean"],
        "train_rank_ic_t": train_stats["t_stat"],
        "test_rank_ic": test_stats["mean"],
        "test_rank_ic_t": test_stats["t_stat"],
        "test_ic_count": test_stats["count"],
        "ann_return": summary["annualized_return"],
        "ann_vol": summary["annualized_volatility"],
        "sharpe": summary["sharpe_ratio"],
        "sortino": summary["sortino_ratio"],
        "max_drawdown": summary["max_drawdown"],
        "hit_rate": summary["hit_rate"],
    }


def main() -> None:
    config = load_config(ROOT / "config/default.yaml")
    setup_logging(config.get("logging", {}).get("level", "INFO"))
    data_cfg = config["data"]
    processed_dir = ensure_dir(ROOT / data_cfg.get("processed_dir", "data/processed"))
    market_data = load_market_data(ROOT / data_cfg.get("market_data_file", "data/raw/ohlcv.csv"))
    benchmark = data_cfg.get("benchmark", "SPY")
    features = build_features(market_data, benchmark=benchmark, **config["features"])

    split_date = config.get("robustness", {}).get("split_date", "2022-01-01")
    quantiles = config["validation"].get("quantiles", 10)
    max_weight = config["portfolio"].get("max_weight", 0.125)
    transaction_cost_bps = config["backtest"].get("transaction_cost_bps", 5.0)

    candidates = [
        {
            "name": "multi_sleeve_blend",
            "base_feature": "blend",
            "direction": "blend",
            "vol_adjust": False,
            "liquidity_threshold": 0.0,
            "horizon": 5,
            "holding_period": 5,
            "sleeves": config["signal"]["sleeves"],
        },
        {
            "name": "default_5d_reversal",
            "base_feature": "return_5d",
            "direction": "reversal",
            "vol_adjust": False,
            "liquidity_threshold": 0.0,
            "horizon": 5,
            "holding_period": 5,
            "sleeves": None,
        },
        {
            "name": "one_day_reversal",
            "base_feature": "return_1d",
            "direction": "reversal",
            "vol_adjust": False,
            "liquidity_threshold": 0.0,
            "horizon": 1,
            "holding_period": 1,
            "sleeves": None,
        },
        {
            "name": "residual_1d_vol_adjusted",
            "base_feature": "residual_1d_return",
            "direction": "reversal",
            "vol_adjust": True,
            "liquidity_threshold": 0.4,
            "horizon": 1,
            "holding_period": 1,
            "sleeves": None,
        },
        {
            "name": "twenty_one_day_momentum",
            "base_feature": "momentum_21d",
            "direction": "momentum",
            "vol_adjust": False,
            "liquidity_threshold": 0.0,
            "horizon": 5,
            "holding_period": 5,
            "sleeves": None,
        },
    ]

    rows = [
        evaluate_candidate(
            market_data=market_data,
            features=features,
            benchmark=benchmark,
            split_date=split_date,
            quantiles=quantiles,
            max_weight=max_weight,
            transaction_cost_bps=transaction_cost_bps,
            **candidate,
        )
        for candidate in candidates
    ]
    pd.DataFrame(rows).to_csv(processed_dir / "robustness_candidates.csv", index=False)

    cost_rows = []
    default = candidates[0]
    alpha = compute_blended_alpha(features, sleeves=default["sleeves"])
    signal = exclude_ticker(alpha["alpha_shifted"], benchmark)
    for bps in [0.0, 2.0, 5.0, 10.0, 20.0]:
        bt = run_long_short_backtest(
            market_data=market_data,
            signal=signal,
            quantiles=quantiles,
            transaction_cost_bps=bps,
            max_weight=max_weight,
            holding_period=default["holding_period"],
        )
        row = bt["summary"].to_dict()
        row["transaction_cost_bps"] = bps
        cost_rows.append(row)
    pd.DataFrame(cost_rows).set_index("transaction_cost_bps").to_csv(processed_dir / "cost_sensitivity.csv")
    print(f"Wrote robustness artifacts to {processed_dir}")


if __name__ == "__main__":
    main()
