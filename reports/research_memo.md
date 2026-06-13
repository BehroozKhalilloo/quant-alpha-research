# Liquidity-Adjusted Reversal Alpha: Research Memo

## Abstract

This project studies a daily cross-sectional US equity alpha based on liquidity-adjusted short-horizon reversal. The current candidate blends five-day reversal, residual one-day reversal, 21-day momentum, and a defensive price/volume quality proxy. The signal is evaluated with shifted signals, forward returns, cross-sectional IC, Newey-West inference, candidate false-discovery checks, transaction costs, capacity estimates, and risk diagnostics.

The sample results are promising but not institutional proof. The free-data version uses yfinance and a static large-cap universe, so survivorship bias and point-in-time limitations remain.

## Research Question

Can short-term cross-sectional dislocations in liquid equities be harvested after accounting for market residualization, liquidity, volatility, turnover, and realistic implementation frictions?

## Falsification Criteria

The signal should be rejected or substantially revised if post-formation tests show unstable or negative out-of-sample rank IC, performance concentrated in a small number of dates, cost-adjusted returns that disappear under moderate transaction costs, capacity estimates that are incompatible with realistic AUM, or factor regressions showing the result is only disguised market, momentum, volatility, or liquidity exposure.

## Economic Intuition

Short-horizon reversal can arise from liquidity provision, temporary price pressure, inventory rebalancing, index-flow spillovers, and overreaction to idiosyncratic news. The effect should be strongest when the stock is liquid enough to trade and the move is not merely broad market beta. It should decay when trading costs rise, when volatility regimes destabilize, when the universe is crowded, or when the move reflects durable information rather than temporary pressure.

## Hypothesis Formation Versus Testing

The research hypothesis is formed before backtesting: recent losers may partially mean-revert, but a pure one-day reversal sleeve may be too noisy. The implemented blend keeps five-day reversal as the dominant sleeve and adds smaller residual reversal, momentum, and defensive quality-proxy components. Robustness tables separate the selected blend from weaker candidate sleeves and report false-discovery-aware statistics.

## Data

The default free-data pipeline uses daily OHLCV from yfinance for a static large-cap US equity universe plus SPY. This is useful for reproducible public research, but it is not a point-in-time institutional database. A production-grade study should use CRSP/Norgate/FactSet-like data with delisting returns, historical identifiers, corporate action audit trails, and point-in-time universe membership.

## Signal Definition

The default signal is:

```text
80%  five-day cross-sectional reversal
10%  residual one-day reversal versus SPY beta
5%   21-day momentum
5%   defensive quality proxy from low realized volatility, liquidity rank, and volume stability
```

Each sleeve is computed using information available at or before the current close. The final alpha is winsorized, cross-sectionally z-scored by date, and shifted one trading day before validation or backtesting.

## Backtest Methodology

The portfolio goes long the top decile and short the bottom decile of shifted alpha, equal-weighted by default, dollar-neutral, and subject to position caps. The default holding period is five trading days using overlapping sub-portfolios. Transaction costs are applied from turnover. Capacity analysis uses ADV participation and a square-root impact proxy.

## Bias Controls

- Signals are shifted before use.
- Forward returns are computed separately from features.
- SPY is excluded from the traded cross-section.
- Static yfinance universe limitations are disclosed.
- Data quality checks flag stale prices, missing fields, extreme returns, and invalid prices.
- Candidate comparison and false-discovery reporting distinguish exploration from evidence.

## Results

See `reports/generated_report.md` for regenerated tables and figures. The latest generated report includes IC summaries, Newey-West inference, backtest statistics, candidate comparison, sleeve ablation, parameter sensitivity, cost sensitivity, capacity, bootstrap confidence intervals, drawdown events, and regime summaries.

## Robustness

The multi-sleeve blend improves portfolio-level metrics versus the pure five-day reversal sleeve in the included sample. Robustness reporting includes sleeve ablation, parameter sensitivity, false-discovery checks, Newey-West inference, purged walk-forward validation, and bootstrap confidence intervals. However, robustness is not uniform: negative 21-day market-trend regimes remain challenging, and capacity estimates deteriorate quickly under square-root impact assumptions.

## Risk Analysis

The report includes gross exposure, net exposure, beta exposure, concentration, rolling Sharpe, rolling drawdown, largest drawdowns, regime performance, and a proxy factor regression. Sector exposure is supported when sector metadata is supplied, but point-in-time sector metadata is not included in the free-data version.

## Transaction Costs and Capacity

Flat bps cost sensitivity is shown alongside square-root impact capacity estimates. The capacity analysis is a proxy, not an execution simulator. It is included to show production awareness and to prevent overinterpretation of frictionless or low-cost returns.

## Limitations

- Static ticker list creates survivorship-bias risk.
- yfinance is not point-in-time institutional data.
- No delisting returns or borrow-cost history.
- No point-in-time sector or fundamental quality data.
- No intraday execution model.
- Results are based on one public-data sample and should be treated as research evidence, not a live trading claim.

## Future Work

1. Replace static universe with point-in-time membership and delisting-aware returns.
2. Add fundamental quality and sector data from point-in-time sources.
3. Add beta/sector-neutral constrained optimization.
4. Add borrow cost and short availability assumptions.
5. Run true out-of-sample validation across broader universes and international markets.

## Trader-Facing Extension

The repository includes fractional Kelly sizing and a simplified Almgren-Chriss execution schedule. These are intentionally separate from the daily alpha backtest and demonstrate expected-value reasoning, position sizing, risk of loss, inventory liquidation, and execution cost trade-offs for stylized trading problems.
