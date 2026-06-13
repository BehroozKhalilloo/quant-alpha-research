# Technical Appendix

## Signal Timing

Features are computed from adjusted close and volume known at date `t`. The signal is shifted one trading day by ticker before validation and backtesting. Forward returns are computed independently as close-to-close returns from `t` to `t+h`.

## Neutralization

Optional cross-sectional neutralization residualizes alpha by date against style exposures: beta, size proxy, volatility, momentum, and liquidity. Sector neutralization is supported through the risk module when point-in-time sector metadata is supplied, but the free-data version does not include sector history.

## Purged Walk-Forward Validation

The purged walk-forward split uses rolling train windows, fixed test windows, and an embargo gap to reduce overlap between feature and forward-return labels.

## Cost And Capacity

Flat bps costs are applied through turnover. Capacity analysis uses a square-root impact proxy:

```text
impact_rate = impact_coefficient * sqrt(dollars_traded / ADV)
```

This is not an execution simulator. It is a conservative sanity check.

## Factor Attribution

The free-data version includes a proxy factor regression using SPY, mega-cap basket returns, and cross-sectional dispersion. Users can provide external Fama-French, q-factor, or proprietary factor files for stronger attribution.

## Trader Extension

The Kelly module evaluates fractional bet sizing under a stylized binary edge. The Almgren-Chriss module computes a simplified execution schedule that trades off temporary impact and inventory risk. Both are scenario tools, not exchange simulators.
