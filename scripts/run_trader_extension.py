#!/usr/bin/env python
"""Run trader-facing Kelly sizing scenario analysis."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant_alpha.trader import almgren_chriss_schedule, kelly_scenario_grid
from quant_alpha.utils import ensure_dir, load_config, setup_logging


def main() -> None:
    config = load_config(ROOT / "config/default.yaml")
    setup_logging(config.get("logging", {}).get("level", "INFO"))
    processed_dir = ensure_dir(ROOT / config["data"].get("processed_dir", "data/processed"))
    trader_cfg = config.get("trader_extension", {})
    result = kelly_scenario_grid(
        win_probability=trader_cfg.get("win_probability", 0.525),
        win_loss_ratio=trader_cfg.get("win_loss_ratio", 1.05),
        fractions=trader_cfg.get("fractions", [0.0, 0.25, 0.5, 0.75, 1.0]),
    )
    result.to_csv(processed_dir / "kelly_sizing_scenarios.csv", index=False)
    execution_cfg = trader_cfg.get("execution", {})
    schedule = almgren_chriss_schedule(
        shares=execution_cfg.get("shares", 100_000),
        intervals=execution_cfg.get("intervals", 20),
        volatility=execution_cfg.get("volatility", 0.02),
        risk_aversion=execution_cfg.get("risk_aversion", 1e-6),
        temporary_impact=execution_cfg.get("temporary_impact", 1e-7),
        permanent_impact=execution_cfg.get("permanent_impact", 0.0),
    )
    schedule.to_csv(processed_dir / "almgren_chriss_schedule.csv", index=False)
    print(f"Wrote trader extension artifacts to {processed_dir}")


if __name__ == "__main__":
    main()
