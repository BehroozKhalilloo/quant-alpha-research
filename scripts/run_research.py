#!/usr/bin/env python
"""Build features, alpha signal, IC statistics, and quantile validation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from quant_alpha.data import load_market_data
from quant_alpha.features import build_features
from quant_alpha.signal import compute_alpha, compute_blended_alpha, naive_reversal_signal
from quant_alpha.utils import ensure_dir, load_config, setup_logging
from quant_alpha.validation import (
    forward_returns,
    information_coefficient,
    pearson_spearman_summary,
    quantile_forward_returns,
    rank_ic_by_year,
)


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
    feature_cfg = config["features"]
    signal_cfg = config["signal"]
    validation_cfg = config["validation"]
    processed_dir = ensure_dir(ROOT / data_cfg.get("processed_dir", "data/processed"))
    data_file = ROOT / data_cfg.get("market_data_file", "data/raw/ohlcv.csv")
    if not data_file.exists():
        raise FileNotFoundError(f"Market data not found at {data_file}. Run python scripts/download_data.py first.")

    market_data = load_market_data(data_file)
    features = build_features(
        market_data,
        benchmark=data_cfg.get("benchmark", "SPY"),
        beta_window=feature_cfg.get("beta_window", 60),
        vol_window=feature_cfg.get("vol_window", 21),
        liquidity_window=feature_cfg.get("liquidity_window", 60),
        volume_window=feature_cfg.get("volume_window", 20),
    )
    alpha = build_alpha(features, signal_cfg)
    horizon = validation_cfg.get("forward_horizon", 1)
    target = forward_returns(market_data, horizon=horizon)
    benchmark = data_cfg.get("benchmark", "SPY")
    signal = exclude_ticker(alpha["alpha_shifted"], benchmark)
    target = exclude_ticker(target, benchmark)
    naive = exclude_ticker(naive_reversal_signal(features, shift_days=signal_cfg.get("shift_days", 1)), benchmark)

    ic_pearson = information_coefficient(signal, target, method="pearson")
    ic_spearman = information_coefficient(signal, target, method="spearman")
    ic_summary = pearson_spearman_summary(signal, target)
    ic_year = rank_ic_by_year(signal, target)
    deciles = quantile_forward_returns(signal, target, quantiles=validation_cfg.get("quantiles", 10))
    naive_ic_summary = pearson_spearman_summary(naive, target)

    features.to_csv(processed_dir / "features.csv")
    alpha.to_csv(processed_dir / "alpha.csv")
    pd.concat([ic_pearson, ic_spearman], axis=1).to_csv(processed_dir / "ic_series.csv")
    ic_summary.to_csv(processed_dir / "ic_summary.csv")
    ic_year.to_csv(processed_dir / "rank_ic_by_year.csv")
    deciles.to_csv(processed_dir / "decile_forward_returns.csv")
    naive_ic_summary.to_csv(processed_dir / "naive_reversal_ic_summary.csv")
    print(f"Wrote research artifacts to {processed_dir}")


if __name__ == "__main__":
    main()
