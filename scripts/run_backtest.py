#!/usr/bin/env python
"""Run the long-short portfolio backtest."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from quant_alpha.backtest import benchmark_returns, run_long_short_backtest
from quant_alpha.data import load_market_data
from quant_alpha.features import build_features
from quant_alpha.metrics import performance_summary
from quant_alpha.risk import exposure_report
from quant_alpha.signal import compute_alpha, compute_blended_alpha, naive_reversal_signal
from quant_alpha.utils import ensure_dir, load_config, setup_logging


def exclude_ticker(series: pd.Series, ticker: str) -> pd.Series:
    """Remove a ticker from a MultiIndex Series."""

    return series[series.index.get_level_values("ticker") != ticker]


def build_alpha(features: pd.DataFrame, signal_cfg: dict) -> pd.DataFrame:
    """Build single-sleeve or blended alpha from config."""

    if signal_cfg.get("mode", "single") == "blend":
        return compute_blended_alpha(
            features,
            sleeves=signal_cfg["sleeves"],
            winsor_lower=signal_cfg.get("winsor_lower", 0.01),
            winsor_upper=signal_cfg.get("winsor_upper", 0.99),
            shift_days=signal_cfg.get("shift_days", 1),
        )
    return compute_alpha(
        features,
        base_feature=signal_cfg.get("base_feature", "residual_1d_return"),
        direction=signal_cfg.get("direction", "reversal"),
        vol_adjust=signal_cfg.get("vol_adjust", True),
        liquidity_threshold=signal_cfg.get("liquidity_threshold", 0.4),
        winsor_lower=signal_cfg.get("winsor_lower", 0.01),
        winsor_upper=signal_cfg.get("winsor_upper", 0.99),
        shift_days=signal_cfg.get("shift_days", 1),
    )


def main() -> None:
    config = load_config(ROOT / "config/default.yaml")
    setup_logging(config.get("logging", {}).get("level", "INFO"))
    data_cfg = config["data"]
    processed_dir = ensure_dir(ROOT / data_cfg.get("processed_dir", "data/processed"))
    data_file = ROOT / data_cfg.get("market_data_file", "data/raw/ohlcv.csv")
    if not data_file.exists():
        raise FileNotFoundError(f"Market data not found at {data_file}. Run python scripts/download_data.py first.")

    market_data = load_market_data(data_file)
    benchmark_ticker = data_cfg.get("benchmark", "SPY")
    features = build_features(market_data, benchmark=benchmark_ticker, **config["features"])
    alpha = build_alpha(features, config["signal"])
    signal = exclude_ticker(alpha["alpha_shifted"], benchmark_ticker)
    naive_signal = exclude_ticker(
        naive_reversal_signal(features, shift_days=config["signal"].get("shift_days", 1)),
        benchmark_ticker,
    )
    result = run_long_short_backtest(
        market_data=market_data,
        signal=signal,
        quantiles=config["validation"].get("quantiles", 10),
        transaction_cost_bps=config["backtest"].get("transaction_cost_bps", 5.0),
        max_weight=config["portfolio"].get("max_weight", 0.10),
        holding_period=config["backtest"].get("holding_period", 1),
        weighting=config["portfolio"].get("weighting", "equal"),
        vol=features["realized_vol_21d"],
    )
    naive = run_long_short_backtest(
        market_data=market_data,
        signal=naive_signal,
        quantiles=config["validation"].get("quantiles", 10),
        transaction_cost_bps=config["backtest"].get("transaction_cost_bps", 5.0),
        max_weight=config["portfolio"].get("max_weight", 0.10),
        holding_period=1,
        weighting="equal",
    )
    benchmark = benchmark_returns(market_data, benchmark=benchmark_ticker)
    risk = exposure_report(result["weights"], beta=features["market_beta"])

    result["weights"].to_csv(processed_dir / "weights.csv")
    pd.concat(
        [
            result["gross_returns"],
            result["net_returns"],
            result["turnover"],
            result["transaction_costs"],
            naive["net_returns"].rename("naive_reversal_net_return"),
            benchmark,
        ],
        axis=1,
    ).to_csv(processed_dir / "backtest_returns.csv")
    result["summary"].to_csv(processed_dir / "backtest_summary.csv")
    performance_summary(naive["net_returns"]).to_csv(processed_dir / "naive_reversal_backtest_summary.csv")
    for name, value in risk.items():
        value.to_csv(processed_dir / f"{name}.csv")
    print(f"Wrote backtest artifacts to {processed_dir}")


if __name__ == "__main__":
    main()
