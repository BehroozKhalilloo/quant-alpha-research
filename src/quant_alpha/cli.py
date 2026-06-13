"""Installed command entry points."""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run_script(name: str) -> None:
    runpy.run_path(str(ROOT / "scripts" / name), run_name="__main__")


def download_data() -> None:
    """Download configured market data."""

    _run_script("download_data.py")


def run_research() -> None:
    """Run feature generation and signal validation."""

    _run_script("run_research.py")


def run_backtest() -> None:
    """Run portfolio backtest."""

    _run_script("run_backtest.py")


def run_robustness() -> None:
    """Run candidate robustness checks."""

    _run_script("run_robustness.py")


def run_diagnostics() -> None:
    """Run advanced diagnostics."""

    _run_script("run_diagnostics.py")


def run_trader_extension() -> None:
    """Run trader-facing Kelly sizing scenario analysis."""

    _run_script("run_trader_extension.py")


def generate_report() -> None:
    """Generate markdown report and figures."""

    _run_script("generate_report.py")
