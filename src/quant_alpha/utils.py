"""Shared configuration, logging, and IO helpers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

LOGGER_NAME = "quant_alpha"


@dataclass(frozen=True)
class ResearchConfig:
    """Typed subset of the YAML configuration used by scripts."""

    tickers: list[str]
    benchmark: str
    start_date: str
    end_date: str | None
    data_dir: Path
    processed_dir: Path
    transaction_cost_bps: float
    max_weight: float
    holding_period: int
    weighting: str
    quantiles: int


def setup_logging(level: str = "INFO") -> None:
    """Configure package logging for command-line scripts."""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def load_config(path: str | Path = "config/default.yaml") -> dict[str, Any]:
    """Load a YAML config file."""

    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def parse_research_config(config: dict[str, Any]) -> ResearchConfig:
    """Convert raw YAML config into a small typed object."""

    data = config["data"]
    backtest = config["backtest"]
    portfolio = config["portfolio"]
    validation = config["validation"]
    return ResearchConfig(
        tickers=list(data["tickers"]),
        benchmark=data.get("benchmark", "SPY"),
        start_date=data["start_date"],
        end_date=data.get("end_date"),
        data_dir=Path(data.get("raw_dir", "data/raw")),
        processed_dir=Path(data.get("processed_dir", "data/processed")),
        transaction_cost_bps=float(backtest.get("transaction_cost_bps", 5.0)),
        max_weight=float(portfolio.get("max_weight", 0.03)),
        holding_period=int(backtest.get("holding_period", 1)),
        weighting=portfolio.get("weighting", "equal"),
        quantiles=int(validation.get("quantiles", 10)),
    )


def ensure_dir(path: str | Path) -> Path:
    """Create a directory if needed and return it as a Path."""

    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def project_root() -> Path:
    """Return the repository root from an installed or source checkout."""

    return Path(__file__).resolve().parents[2]

