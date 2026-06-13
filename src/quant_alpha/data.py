"""Market data loading and provider abstraction."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

LOGGER = logging.getLogger(__name__)


REQUIRED_COLUMNS = ["open", "high", "low", "close", "adj_close", "volume"]


class MarketDataProvider(ABC):
    """Interface for daily OHLCV data providers."""

    @abstractmethod
    def download(
        self,
        tickers: list[str],
        start: str,
        end: str | None = None,
    ) -> pd.DataFrame:
        """Return long-form OHLCV data indexed by date and ticker."""


class YFinanceProvider(MarketDataProvider):
    """Download adjusted daily OHLCV data from yfinance."""

    def download(
        self,
        tickers: list[str],
        start: str,
        end: str | None = None,
    ) -> pd.DataFrame:
        import yfinance as yf

        LOGGER.info("Downloading %d tickers from yfinance", len(tickers))
        raw = yf.download(
            tickers=tickers,
            start=start,
            end=end,
            auto_adjust=False,
            group_by="ticker",
            progress=False,
            threads=True,
        )
        return normalize_yfinance(raw, tickers)


def normalize_yfinance(raw: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """Normalize yfinance output into a long OHLCV DataFrame."""

    frames: list[pd.DataFrame] = []
    for ticker in tickers:
        if isinstance(raw.columns, pd.MultiIndex):
            if ticker not in raw.columns.get_level_values(0):
                LOGGER.warning("Ticker %s missing from download", ticker)
                continue
            frame = raw[ticker].copy()
        else:
            frame = raw.copy()
        if frame.empty:
            continue
        frame = frame.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )
        frame["ticker"] = ticker
        frames.append(frame[[*REQUIRED_COLUMNS, "ticker"]])

    if not frames:
        raise ValueError("No market data returned")

    out = pd.concat(frames)
    out.index = pd.to_datetime(out.index).tz_localize(None)
    out.index.name = "date"
    out = out.reset_index().set_index(["date", "ticker"]).sort_index()
    return out.dropna(subset=["adj_close", "volume"])


def save_market_data(data: pd.DataFrame, path: str | Path) -> None:
    """Persist market data as parquet when possible, otherwise CSV."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".parquet":
        data.to_parquet(path)
    else:
        data.to_csv(path)


def load_market_data(path: str | Path) -> pd.DataFrame:
    """Load long-form OHLCV data from parquet or CSV."""

    path = Path(path)
    if path.suffix == ".parquet":
        data = pd.read_parquet(path)
    else:
        data = pd.read_csv(path, parse_dates=["date"])
        data = data.set_index(["date", "ticker"])
    data.index = data.index.set_levels(
        [pd.to_datetime(data.index.levels[0]), data.index.levels[1]]
    )
    return data.sort_index()


def get_provider(name: str) -> MarketDataProvider:
    """Factory for market data providers."""

    normalized = name.lower()
    if normalized in {"yfinance", "yf"}:
        return YFinanceProvider()
    raise ValueError(f"Unsupported data provider: {name}")

