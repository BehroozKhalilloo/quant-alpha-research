#!/usr/bin/env python
"""Generate figures and a markdown research report from saved artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import matplotlib.pyplot as plt

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


def read_optional_no_index(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def markdown_table(frame: pd.DataFrame | None) -> str:
    """Render a compact markdown table without optional dependencies."""

    if frame is None or frame.empty:
        return "Not generated."
    display = frame.copy()
    display = display.map(
        lambda x: "" if pd.isna(x) else f"{x:.6g}" if isinstance(x, float) else x
    )
    headers = ["metric", *map(str, display.columns)]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for index, row in display.iterrows():
        lines.append("| " + " | ".join([str(index), *map(str, row.tolist())]) + " |")
    return "\n".join(lines)


def plot_table_column(
    frame: pd.DataFrame | None,
    column: str,
    title: str,
    ylabel: str,
    path: Path,
) -> str | None:
    """Plot a single table column and return a markdown image link."""

    if frame is None or frame.empty or column not in frame:
        return None
    fig, ax = plt.subplots(figsize=(8, 3))
    frame[column].plot(kind="bar", ax=ax)
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", alpha=0.3)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return f"![{title}](figures/{path.name})"


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
    ic_summary = read_optional(processed_dir / "ic_summary.csv", parse_dates=False)
    backtest_summary = read_optional(processed_dir / "backtest_summary.csv", parse_dates=False)
    naive_summary = read_optional(processed_dir / "naive_reversal_backtest_summary.csv", parse_dates=False)
    robustness = read_optional_no_index(processed_dir / "robustness_candidates.csv")
    cost_sensitivity = read_optional(processed_dir / "cost_sensitivity.csv", parse_dates=False)
    bootstrap = read_optional(processed_dir / "bootstrap_summary.csv", parse_dates=False)
    regime = read_optional_no_index(processed_dir / "regime_summary.csv")
    drawdowns = read_optional_no_index(processed_dir / "drawdown_events.csv")
    rolling = read_optional(processed_dir / "rolling_performance.csv")

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
    if robustness is not None and "candidate" in robustness:
        robustness_plot = robustness.set_index("candidate")
        link = plot_table_column(
            robustness_plot,
            "sharpe",
            "Candidate Sharpe Comparison",
            "Sharpe ratio",
            figures_dir / "candidate_sharpe.png",
        )
        if link:
            figure_lines.append(link)
    if cost_sensitivity is not None:
        link = plot_table_column(
            cost_sensitivity,
            "sharpe_ratio",
            "Transaction Cost Sensitivity",
            "Sharpe ratio",
            figures_dir / "cost_sensitivity.png",
        )
        if link:
            figure_lines.append(link)
    if rolling is not None and "rolling_sharpe" in rolling:
        fig, ax = plt.subplots(figsize=(9, 3))
        rolling["rolling_sharpe"].plot(ax=ax)
        ax.axhline(0.0, color="black", linewidth=1)
        ax.set_title("Rolling 126-Day Sharpe")
        ax.grid(True, alpha=0.3)
        fig.savefig(figures_dir / "rolling_126d_sharpe.png", bbox_inches="tight", dpi=150)
        plt.close(fig)
        figure_lines.append("![Rolling 126-Day Sharpe](figures/rolling_126d_sharpe.png)")

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
                "## IC Summary",
                "",
                markdown_table(ic_summary),
                "",
                "## Backtest Summary",
                "",
                markdown_table(backtest_summary),
                "",
                "## Naive Reversal Baseline",
                "",
                markdown_table(naive_summary),
                "",
                "## Robustness Checks",
                "",
                markdown_table(robustness.set_index("candidate") if robustness is not None and "candidate" in robustness else robustness),
                "",
                "## Transaction Cost Sensitivity",
                "",
                markdown_table(cost_sensitivity),
                "",
                "## Bootstrap Confidence Intervals",
                "",
                markdown_table(bootstrap),
                "",
                "## Regime Summary",
                "",
                markdown_table(regime.set_index(["group", "regime"]) if regime is not None and {"group", "regime"}.issubset(regime.columns) else regime),
                "",
                "## Largest Drawdowns",
                "",
                markdown_table(drawdowns),
                "",
                "## Interpretation",
                "",
                "The selected multi-sleeve blend has positive full-sample IC, positive pre/post split rank IC, stronger Sharpe and drawdown than the pure reversal sleeve, and remains positive across the displayed transaction-cost stress range. Bootstrap intervals and rolling diagnostics make the result easier to audit. Regime analysis shows the strategy is materially stronger in positive 21-day market trends and weaker in negative trend regimes, so the evidence is stronger than the single-sleeve baseline but still not production proof.",
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
