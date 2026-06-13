# Cross-Sectional Equity Alpha Research: Liquidity-Adjusted Reversal

## Abstract

This memo studies a daily cross-sectional equity signal that looks for short-term mean reversion after unusually negative returns, conditional on sufficient liquidity and controlled portfolio construction. The project is structured as a reproducible research pipeline rather than a trading system.

## Hypothesis

Short-horizon residual underperformance can partially reverse when the price move occurs in sufficiently liquid names and is not dominated by volatility noise. The signal should be evaluated cross-sectionally using next-period returns, IC statistics, quantile spreads, turnover, transaction costs, and exposure diagnostics.

## Data

The default universe is a configurable list of liquid US large-cap equities plus SPY as the benchmark. Daily OHLCV data is downloaded through the modular provider interface, with yfinance configured by default.

The analysis should be read with standard caveats: the default ticker list is not point-in-time, corporate action handling depends on the vendor, and delisted securities are not represented unless the user supplies a survivorship-bias-controlled dataset.

## Signal Construction

For each stock and date, the pipeline computes one-day return, five-day return, 21-day momentum, 21-day realized volatility, dollar volume, liquidity rank, volume shock, rolling market beta versus SPY, and residual one-day return. The default alpha starts from negative cross-sectional five-day return, applies liquidity eligibility, winsorizes cross-sectionally, z-scores by date, and shifts the signal forward one trading day before validation or backtesting. The original one-day residual reversal with volatility adjustment remains available as a configurable specification.

## Validation Results Placeholder

After running `python scripts/run_research.py`, this section can be populated with realized Pearson IC, Spearman rank IC, IC t-statistics, rank IC by year, and decile forward-return spreads.

No numerical performance claims are included in this template.

## Backtest Results Placeholder

After running `python scripts/run_backtest.py`, this section can be populated with long-short daily returns, turnover, transaction costs, drawdown, Sharpe ratio, Sortino ratio, annualized volatility, max drawdown, and benchmark comparison against SPY and a naive reversal baseline.

## Risk Analysis

The backtest records gross exposure, net exposure, beta exposure versus SPY, and concentration. Sector exposure can be added when point-in-time sector metadata is supplied.

## Limitations

The default universe is not survivorship-bias free. yfinance adjusted prices are convenient for research but are not an institutional-grade point-in-time database. Results are sensitive to the universe, sample window, transaction costs, liquidity filters, rebalance assumptions, and missing-data handling.

## Next Steps

Add a point-in-time survivorship-bias-controlled universe, robust corporate action validation, sector-neutral scoring, borrow-cost assumptions for shorts, cross-validation across market regimes, and parameter-sensitivity studies.
