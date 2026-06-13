#!/usr/bin/env python
"""Generate advanced diagnostics from saved backtest artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from quant_alpha.diagnostics import (
    block_bootstrap_summary,
    drawdown_events,
    monthly_return_table,
    regime_summary,
    rolling_performance,
)
from quant_alpha.utils import ensure_dir, load_config, setup_logging


def main() -> None:
    config = load_config(ROOT / "config/default.yaml")
    setup_logging(config.get("logging", {}).get("level", "INFO"))
    processed_dir = ensure_dir(ROOT / config["data"].get("processed_dir", "data/processed"))
    returns_path = processed_dir / "backtest_returns.csv"
    if not returns_path.exists():
        raise FileNotFoundError("Run python scripts/run_backtest.py before diagnostics.")

    returns = pd.read_csv(returns_path, index_col=0, parse_dates=True)
    strategy = returns["net_return"]
    benchmark_col = next((col for col in returns.columns if col.endswith("_return")), None)
    if benchmark_col is None:
        raise ValueError("Benchmark return column not found in backtest_returns.csv")

    block_bootstrap_summary(strategy).to_csv(processed_dir / "bootstrap_summary.csv")
    rolling_performance(strategy).to_csv(processed_dir / "rolling_performance.csv")
    monthly_return_table(strategy).to_csv(processed_dir / "monthly_returns.csv")
    regime_summary(strategy, returns[benchmark_col]).to_csv(processed_dir / "regime_summary.csv", index=False)
    drawdown_events(strategy).to_csv(processed_dir / "drawdown_events.csv", index=False)
    print(f"Wrote diagnostics artifacts to {processed_dir}")


if __name__ == "__main__":
    main()

