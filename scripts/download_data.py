#!/usr/bin/env python
"""Download configured daily OHLCV data."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant_alpha.data import get_provider, save_market_data
from quant_alpha.utils import load_config, setup_logging


def main() -> None:
    config = load_config(ROOT / "config/default.yaml")
    setup_logging(config.get("logging", {}).get("level", "INFO"))
    data_cfg = config["data"]

    tickers = sorted(set(data_cfg["tickers"] + [data_cfg.get("benchmark", "SPY")]))
    provider = get_provider(data_cfg.get("provider", "yfinance"))
    data = provider.download(
        tickers=tickers,
        start=data_cfg["start_date"],
        end=data_cfg.get("end_date"),
    )
    output = ROOT / data_cfg.get("market_data_file", "data/raw/ohlcv.csv")
    save_market_data(data, output)
    print(f"Saved {len(data):,} rows to {output}")


if __name__ == "__main__":
    main()

