# Cross-Sectional Equity Alpha Research: Liquidity-Adjusted Reversal Signal

This repository is a reproducible quant research project for a daily cross-sectional US equity alpha signal. It is designed to show signal design, data engineering, statistical validation, portfolio construction, transaction-cost-aware backtesting, risk checks, and clear research communication.

It is not a live trading system, broker integration, or investment recommendation.

## Why This Project Matters

Quant research work is not just writing a return formula. A credible research workflow needs a clean data contract, explicit bias controls, careful signal timing, validation metrics, portfolio construction assumptions, and honest reporting. This repo is structured around that workflow.

The implementation avoids toy moving-average crossover logic. The signal is cross-sectional, residualized against the market, liquidity-aware, volatility-adjusted, and evaluated with IC, decile spreads, long-short returns, turnover, drawdown, and exposure diagnostics.

## Signal Hypothesis

Stocks with unusually negative short-term residual returns may mean-revert over the next trading day or several days. The effect is expected to be more credible when:

- the move is measured after removing market return using a rolling beta estimate;
- the stock is sufficiently liquid;
- the signal is scaled by realized volatility so high-noise names do not dominate;
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

Main alpha construction:

```text
alpha_raw = -zscore_cross_section(residual_1d_return)
alpha_vol_adj = alpha_raw / realized_vol_21d
alpha = alpha_vol_adj * liquidity_filter
alpha = winsorize_cross_section(alpha)
alpha = zscore_cross_section(alpha)
alpha_shifted = alpha shifted by one trading day per ticker
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

Forward returns are computed from close at date `t` to close at date `t+h`. The prediction target is configurable through `config/default.yaml`.

## Backtest Assumptions

The backtest is vectorized and daily:

- long top signal decile and short bottom signal decile;
- equal-weight by default, with optional volatility-scaled weights;
- dollar-neutral construction;
- gross exposure target of approximately 1.0;
- individual position cap;
- configurable holding period of 1 or 5 days;
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
data/processed/weights.csv
reports/generated_report.md
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

## Limitations

This is a research repo. It is suitable for demonstrating a disciplined research process, but it is not production portfolio infrastructure. Before relying on any result, a researcher should use point-in-time data, survivorship-bias-free universes, robust corporate action checks, realistic financing and borrow assumptions, and stronger out-of-sample validation.

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

