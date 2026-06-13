#!/usr/bin/env python
"""Build features, alpha signal, IC statistics, and quantile validation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
from scipy import stats

from quant_alpha.data import load_market_data
from quant_alpha.data_quality import (
    apply_point_in_time_universe,
    load_universe_membership,
    summarize_quality_report,
    validate_market_data,
)
from quant_alpha.features import build_features
from quant_alpha.signal import apply_alpha_neutralization, compute_alpha, compute_blended_alpha, naive_reversal_signal
from quant_alpha.stats import false_discovery_report, newey_west_mean_test
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
        alpha = compute_blended_alpha(
            features,
            sleeves=signal_cfg["sleeves"],
            winsor_lower=signal_cfg.get("winsor_lower", 0.01),
            winsor_upper=signal_cfg.get("winsor_upper", 0.99),
            shift_days=signal_cfg.get("shift_days", 1),
        )
    else:
        alpha = compute_alpha(
            features,
            base_feature=signal_cfg.get("base_feature", "residual_1d_return"),
            direction=signal_cfg.get("direction", "reversal"),
            vol_adjust=signal_cfg.get("vol_adjust", True),
            liquidity_threshold=signal_cfg.get("liquidity_threshold", 0.4),
            winsor_lower=signal_cfg.get("winsor_lower", 0.01),
            winsor_upper=signal_cfg.get("winsor_upper", 0.99),
            shift_days=signal_cfg.get("shift_days", 1),
        )
    neutral_cfg = signal_cfg.get("neutralize", {})
    if neutral_cfg.get("enabled", False):
        alpha = apply_alpha_neutralization(alpha, features, neutral_cfg.get("columns", []))
    return alpha


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
    quality_reports = validate_market_data(market_data)
    summarize_quality_report(quality_reports).to_csv(processed_dir / "data_quality_summary.csv", index=False)
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
    membership_file = data_cfg.get("universe_membership_file")
    if membership_file:
        membership = load_universe_membership(str(ROOT / membership_file))
        signal = apply_point_in_time_universe(signal, membership)
        naive = apply_point_in_time_universe(naive, membership)

    ic_pearson = information_coefficient(signal, target, method="pearson")
    ic_spearman = information_coefficient(signal, target, method="spearman")
    ic_summary = pearson_spearman_summary(signal, target)
    nw_ic = pd.DataFrame(
        {
            "pearson": newey_west_mean_test(ic_pearson, lags=horizon),
            "spearman": newey_west_mean_test(ic_spearman, lags=horizon),
        }
    ).T
    ic_year = rank_ic_by_year(signal, target)
    deciles = quantile_forward_returns(signal, target, quantiles=validation_cfg.get("quantiles", 10))
    naive_ic_summary = pearson_spearman_summary(naive, target)
    candidate_p_values = pd.Series(
        {
            "pearson_ic": 2.0 * (1.0 - stats.norm.cdf(abs(ic_summary.loc["pearson", "t_stat"]))),
            "spearman_ic": 2.0 * (1.0 - stats.norm.cdf(abs(ic_summary.loc["spearman", "t_stat"]))),
        }
    )
    false_discovery_report(candidate_p_values).to_csv(processed_dir / "false_discovery_report.csv")

    features.to_csv(processed_dir / "features.csv")
    alpha.to_csv(processed_dir / "alpha.csv")
    pd.concat([ic_pearson, ic_spearman], axis=1).to_csv(processed_dir / "ic_series.csv")
    ic_summary.to_csv(processed_dir / "ic_summary.csv")
    nw_ic.to_csv(processed_dir / "newey_west_ic_summary.csv")
    ic_year.to_csv(processed_dir / "rank_ic_by_year.csv")
    deciles.to_csv(processed_dir / "decile_forward_returns.csv")
    naive_ic_summary.to_csv(processed_dir / "naive_reversal_ic_summary.csv")
    print(f"Wrote research artifacts to {processed_dir}")


if __name__ == "__main__":
    main()
