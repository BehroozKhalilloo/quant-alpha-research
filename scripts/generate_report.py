#!/usr/bin/env python
"""Generate figures and a markdown research report from saved artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from quant_alpha.plotting import (
    plot_beta_exposure,
    plot_cumulative_returns,
    plot_decile_forward_returns,
    plot_drawdown,
    plot_ic_by_year,
    plot_ic_time_series,
    plot_rolling_sharpe,
    plot_turnover,
)
from quant_alpha.utils import ensure_dir, load_config, setup_logging


def read_optional(path: Path, parse_dates: bool = True) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path, index_col=0, parse_dates=parse_dates)


def main() -> None:
    config = load_config(ROOT / "config/default.yaml")
    setup_logging(config.get("logging", {}).get("level", "INFO"))
    processed_dir = ROOT / config["data"].get("processed_dir", "data/processed")
    report_cfg = config["report"]
    figures_dir = ensure_dir(ROOT / report_cfg.get("figures_dir", "reports/figures"))
    output_file = ROOT / report_cfg.get("output_file", "reports/generated_report.md")

    returns = read_optional(processed_dir / "backtest_returns.csv")
    ic = read_optional(processed_dir / "ic_series.csv")
    ic_year = read_optional(processed_dir / "rank_ic_by_year.csv", parse_dates=False)
    deciles = read_optional(processed_dir / "decile_forward_returns.csv", parse_dates=False)
    beta = read_optional(processed_dir / "beta_exposure.csv")

    figure_lines: list[str] = []
    if returns is not None and "net_return" in returns:
        plot_cumulative_returns(returns["net_return"], figures_dir / "cumulative_returns.png")
        plot_drawdown(returns["net_return"], figures_dir / "drawdown.png")
        plot_rolling_sharpe(returns["net_return"], path=figures_dir / "rolling_sharpe.png")
        plot_turnover(returns["turnover"], figures_dir / "turnover.png")
        figure_lines.extend(
            [
                "![Cumulative returns](figures/cumulative_returns.png)",
                "![Drawdown](figures/drawdown.png)",
                "![Rolling Sharpe](figures/rolling_sharpe.png)",
                "![Turnover](figures/turnover.png)",
            ]
        )
    if ic is not None and "spearman_ic" in ic:
        plot_ic_time_series(ic["spearman_ic"], figures_dir / "ic_time_series.png")
        figure_lines.append("![IC time series](figures/ic_time_series.png)")
    if ic_year is not None:
        series = ic_year.iloc[:, 0] if isinstance(ic_year, pd.DataFrame) else ic_year
        plot_ic_by_year(series, figures_dir / "ic_by_year.png")
        figure_lines.append("![IC by year](figures/ic_by_year.png)")
    if deciles is not None and "mean" in deciles:
        plot_decile_forward_returns(deciles, figures_dir / "decile_forward_returns.png")
        figure_lines.append("![Decile forward returns](figures/decile_forward_returns.png)")
    if beta is not None:
        plot_beta_exposure(beta.iloc[:, 0], figures_dir / "beta_exposure.png")
        figure_lines.append("![Beta exposure](figures/beta_exposure.png)")

    output_file.write_text(
        "\n".join(
            [
                "# Liquidity-Adjusted Reversal Research Report",
                "",
                "This report is generated from local research artifacts. It intentionally does not hard-code performance claims.",
                "",
                "## Generated Figures",
                "",
                "\n\n".join(figure_lines) if figure_lines else "No figures generated yet. Run research and backtest first.",
                "",
                "## Interpretation",
                "",
                "Review IC stability, decile monotonicity, turnover, drawdowns, and beta exposure before drawing any conclusion. Results depend on the configured universe, sample period, transaction costs, and data quality.",
                "",
                "## Disclaimer",
                "",
                "This repository is for research and education only. It is not investment advice and does not include live trading or broker execution.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote report to {output_file}")


if __name__ == "__main__":
    main()
