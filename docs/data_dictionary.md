# Data Dictionary

## Market Data

The free-data version expects long-form daily OHLCV data indexed by `date, ticker`.

| Column | Meaning | Point-in-time caveat |
| --- | --- | --- |
| `open` | Daily open price | Vendor adjusted treatment may vary |
| `high` | Daily high price | Vendor adjusted treatment may vary |
| `low` | Daily low price | Vendor adjusted treatment may vary |
| `close` | Daily close price | Raw close can be affected by corporate actions |
| `adj_close` | Adjusted close used for returns | yfinance adjustments are convenient but not institutional point-in-time data |
| `volume` | Daily share volume | Does not include venue-level microstructure detail |

## Optional Point-In-Time Universe

Users with CRSP, Norgate, FactSet, Polygon, or internal data can provide a membership file:

| Column | Meaning |
| --- | --- |
| `date` | Trading date |
| `ticker` | Security identifier used by the market data file |
| `in_universe` | Boolean membership flag known at that date |

The default yfinance universe is not survivorship-bias free. A serious institutional study should replace it with point-in-time membership and delisting-aware returns.

## Processed Features

| Feature | Definition |
| --- | --- |
| `return_1d` | Adjusted close daily return |
| `return_5d` | Five-trading-day adjusted close return |
| `momentum_21d` | 21-trading-day adjusted close return |
| `realized_vol_21d` | Rolling 21-day daily return standard deviation |
| `dollar_volume` | Adjusted close times share volume |
| `liquidity_rank` | Rolling within-name dollar-volume percentile |
| `volume_shock` | Volume divided by rolling 20-day average volume |
| `market_beta` | Rolling beta versus SPY |
| `residual_1d_return` | One-day return minus rolling beta times SPY return |

