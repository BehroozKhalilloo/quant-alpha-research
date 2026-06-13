# Cross-Sectional Equity Alpha Research: Liquidity-Adjusted Reversal Signal

This repository is a reproducible quant research project for a daily cross-sectional US equity alpha signal. It is designed to show signal design, data engineering, statistical validation, portfolio construction, transaction-cost-aware backtesting, robustness analysis, risk checks, and clear research communication.

It is not a live trading system, broker integration, or investment recommendation.

## Why This Project Matters

Quant research work is not just writing a return formula. A credible research workflow needs a clean data contract, explicit bias controls, careful signal timing, validation metrics, portfolio construction assumptions, and honest reporting. This repo is structured around that workflow.

For an interviewer, the point of this project is not that a public-data daily equity signal is ready to trade. The point is that the research process exposes assumptions, tests failure modes, measures capacity and costs, and keeps the implementation reproducible.

The implementation avoids toy moving-average crossover logic. The signal is cross-sectional, liquidity-aware, configurable across reversal specifications, and evaluated with IC, decile spreads, long-short returns, turnover, drawdown, transaction-cost sensitivity, train/test splits, bootstrap confidence intervals, regime diagnostics, and exposure diagnostics.

The current default candidate is a pre-specified multi-sleeve blend: five-day reversal, residual one-day reversal, 21-day momentum, and a defensive price/volume quality proxy. In the included sample it improves the portfolio profile versus the pure five-day reversal sleeve: higher full-sample IC, higher Sharpe, lower drawdown, and better transaction-cost robustness. The repo is built to make those claims auditable rather than hand-waved.

## Signal Hypothesis

Stocks with unusually negative short-term returns may mean-revert over the next several trading days. The default candidate uses five-day cross-sectional reversal as the dominant sleeve, then blends smaller residual reversal, momentum, and defensive quality-proxy sleeves to reduce path risk. The original one-day residual reversal variant is still configurable and useful as a stricter hypothesis test.

The effect is expected to be more credible when:

- the move is not just broad market exposure;
- the stock is sufficiently liquid;
- high-noise names do not dominate the portfolio;
- the portfolio is dollar-neutral and constrained.

The project tests this hypothesis. It does not assume it is true.

## Data

The default config uses approximately 50 liquid US large-cap tickers plus `SPY` as the benchmark. Daily OHLCV data is downloaded through a provider interface in `src/quant_alpha/data.py`; `yfinance` is the default provider, and the interface is intentionally small so Stooq or another vendor can be added later.

Expected market data format is long-form:

```text
index: date, ticker
columns: open, high, low, close, adj_close, volume
```

Raw downloaded data is written to `data/raw/ohlcv.csv`. Processed research artifacts are written to `data/processed/`.

## Methodology

Feature construction uses only information known at or before each date close:

- one-day return;
- five-day return;
- 21-day momentum;
- 21-day realized volatility;
- dollar volume;
- rolling dollar-volume percentile;
- volume shock versus 20-day average;
- rolling market beta versus `SPY`;
- residual one-day return after removing market return.

Main alpha construction is configurable through `config/default.yaml`. The current default is a fixed-weight blend:

```text
80%  five-day reversal
10%  residual one-day reversal
5%   21-day momentum
5%   defensive quality proxy from low volatility, liquidity rank, and volume stability

alpha = zscore_cross_section(weighted sleeve blend)
alpha_shifted = alpha shifted by one trading day per ticker
```

The quality sleeve is not a fundamental quality factor because the default data source does not include point-in-time fundamentals. It is a defensive price/volume proxy. Alternative specifications include one-day residual reversal with volatility adjustment:

```text
base_feature = residual_1d_return
alpha_raw = -zscore_cross_section(base_feature)
alpha = alpha_raw / realized_vol_21d
```

The shifted signal is used for validation and backtesting to reduce look-ahead risk.

## Validation

`scripts/run_research.py` computes:

- Pearson IC;
- Spearman rank IC;
- IC mean, standard deviation, t-statistic, and observation count;
- rank IC by year;
- decile forward-return means;
- naive one-day reversal baseline IC.

`scripts/run_robustness.py` adds:

- candidate comparison across the multi-sleeve blend, pure reversal, residual reversal, and momentum variants;
- pre/post split rank IC using the configured split date;
- transaction-cost sensitivity for the selected default;
- evidence that the selected candidate improves portfolio-level metrics versus weaker baseline variants.

`scripts/run_diagnostics.py` adds:

- moving-block bootstrap confidence intervals;
- rolling 126-day performance diagnostics;
- monthly return table;
- largest drawdown events;
- performance by simple market and volatility regimes.

Additional research controls now include:

- data quality checks for missing fields, nonpositive prices, zero volume, stale prices, and extreme returns;
- Newey-West autocorrelation-robust IC inference;
- false-discovery-aware candidate reporting;
- sleeve ablation tests;
- parameter sensitivity across signal definitions, liquidity thresholds, and volatility scaling;
- capacity estimates using ADV participation and a square-root impact proxy.
- purged walk-forward validation;
- optional style neutralization against beta, size proxy, volatility, momentum, and liquidity;
- proxy factor regression and hooks for user-supplied factor files;
- a trader-facing fractional Kelly sizing module.

Forward returns are computed from close at date `t` to close at date `t+h`. The prediction target is configurable through `config/default.yaml`.

## Backtest Assumptions

The backtest is vectorized and daily:

- long top signal decile and short bottom signal decile;
- equal-weight by default, with optional volatility-scaled weights;
- dollar-neutral construction;
- gross exposure target of approximately 1.0;
- individual position cap;
- configurable holding period, with 5 days used by default;
- transaction costs applied from one-way turnover in basis points;
- shifted signal at date `t` is applied to the next available close-to-close return.

The backtest compares the liquidity-adjusted reversal signal against `SPY` and a naive cross-sectional one-day reversal baseline.

## Metrics Explained

- **Information coefficient:** daily cross-sectional correlation between signal and forward returns.
- **Rank IC:** Spearman IC, less sensitive to outliers than Pearson correlation.
- **IC t-stat:** mean IC divided by IC standard error.
- **Decile spread:** average top-decile forward return minus bottom-decile forward return.
- **Turnover:** one-way daily portfolio weight change.
- **Sharpe ratio:** annualized mean daily return divided by annualized volatility, zero risk-free rate.
- **Sortino ratio:** Sharpe-like ratio using downside volatility.
- **Max drawdown:** worst peak-to-trough decline of compounded long-short returns.
- **Beta exposure:** weighted rolling beta exposure versus `SPY`.
- **Concentration:** Herfindahl-style concentration based on absolute weights.

## Bias Controls

The code explicitly addresses:

- signal shifting before validation and backtesting;
- forward-return construction that keeps targets separate from features;
- missing data handling through aligned pandas operations;
- transaction costs using turnover;
- dollar-neutral and gross-exposure sanity checks;
- max position weight checks;
- benchmark beta exposure monitoring.

Important caveats remain:

- the default ticker list is not survivorship-bias controlled;
- yfinance is convenient but not point-in-time institutional data;
- corporate action quality depends on the vendor;
- sector-neutral scoring requires external sector metadata;
- borrow costs, short availability, taxes, and intraday execution are not modeled.

## Install

```bash
cd quant-alpha-research
python -m venv .venv
source .venv/bin/activate
make install
```

Equivalent direct install:

```bash
python -m pip install -e ".[dev]"
```

## Run

Download data:

```bash
make data
```

Run signal validation:

```bash
make research
```

Run backtest:

```bash
make backtest
```

Generate report figures and markdown:

```bash
make robustness
make diagnostics
make trader
make report
```

Run tests:

```bash
make test
```

Direct script equivalents:

```bash
python scripts/download_data.py
python scripts/run_research.py
python scripts/run_backtest.py
python scripts/run_robustness.py
python scripts/run_diagnostics.py
python scripts/run_trader_extension.py
python scripts/generate_report.py
pytest
```

## Example Outputs

After running the pipeline, expected artifacts include:

```text
data/processed/features.csv
data/processed/alpha.csv
data/processed/ic_series.csv
data/processed/ic_summary.csv
data/processed/rank_ic_by_year.csv
data/processed/decile_forward_returns.csv
data/processed/backtest_returns.csv
data/processed/backtest_summary.csv
data/processed/robustness_candidates.csv
data/processed/cost_sensitivity.csv
data/processed/bootstrap_summary.csv
data/processed/rolling_performance.csv
data/processed/monthly_returns.csv
data/processed/regime_summary.csv
data/processed/drawdown_events.csv
data/processed/data_quality_summary.csv
data/processed/newey_west_ic_summary.csv
data/processed/false_discovery_report.csv
data/processed/candidate_false_discovery.csv
data/processed/sleeve_ablation.csv
data/processed/parameter_sensitivity.csv
data/processed/capacity_summary.csv
data/processed/purged_walk_forward.csv
data/processed/factor_regression_proxy.csv
data/processed/kelly_sizing_scenarios.csv
data/processed/weights.csv
reports/generated_report.md
reports/research_memo.md
reports/figures/*.png
```

The repository does not ship fabricated performance tables. `reports/sample_report.md` contains placeholders such as: “After running `python scripts/run_research.py`, this table will populate with realized IC statistics.”

## Configuration

Edit `config/default.yaml` to change:

- universe and benchmark;
- date range;
- data provider;
- beta, volatility, liquidity, and volume windows;
- liquidity threshold;
- forward-return horizon;
- number of quantiles;
- weighting method;
- max position weight;
- holding period;
- transaction cost in basis points.
- robustness split date.

## Limitations

This is a research repo. It is suitable for demonstrating a disciplined research process, but it is not production portfolio infrastructure. Before relying on any result, a researcher should use point-in-time data, survivorship-bias-free universes, robust corporate action checks, realistic financing and borrow assumptions, and stronger out-of-sample validation.

The included capacity analysis is deliberately conservative. Under the square-root impact proxy, the strategy is capacity-limited unless execution assumptions, universe breadth, or turnover controls improve. This is a feature of the research process, not a hidden footnote.

## Future Improvements

- Add Stooq or institutional data adapters.
- Add point-in-time sector and industry metadata.
- Add sector-neutral and beta-neutral optimization.
- Add borrow-cost and short-availability assumptions.
- Add parameter sensitivity and walk-forward validation.
- Add market-regime analysis.
- Add richer report tables once real data is generated locally.

## Disclaimer

This project is for research and educational purposes only. It is not financial advice, investment advice, or a recommendation to buy or sell any security. It does not include live trading, broker execution, or order management.
