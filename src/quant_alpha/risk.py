"""Risk and exposure diagnostics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def gross_exposure(weights: pd.DataFrame) -> pd.Series:
    """Gross exposure by date."""

    return weights.abs().sum(axis=1).rename("gross_exposure")


def net_exposure(weights: pd.DataFrame) -> pd.Series:
    """Net exposure by date."""

    return weights.sum(axis=1).rename("net_exposure")


def concentration(weights: pd.DataFrame) -> pd.Series:
    """Herfindahl concentration based on absolute weights."""

    abs_weights = weights.abs()
    gross = abs_weights.sum(axis=1).replace(0.0, np.nan)
    return ((abs_weights.div(gross, axis=0) ** 2).sum(axis=1)).rename("concentration")


def beta_exposure(weights: pd.DataFrame, beta: pd.Series | pd.DataFrame) -> pd.Series:
    """Portfolio beta exposure versus benchmark."""

    beta_wide = beta.unstack("ticker") if isinstance(beta, pd.Series) else beta
    aligned_beta = beta_wide.reindex_like(weights)
    return (weights * aligned_beta).sum(axis=1).rename("beta_exposure")


def sector_exposure(weights: pd.DataFrame, sector_map: dict[str, str]) -> pd.DataFrame:
    """Aggregate portfolio weights by sector."""

    sectors = pd.Series(sector_map)
    available = [col for col in weights.columns if col in sectors.index]
    if not available:
        return pd.DataFrame(index=weights.index)
    mapped = weights[available].T.groupby(sectors.loc[available]).sum().T
    mapped.index.name = "date"
    return mapped


def exposure_report(
    weights: pd.DataFrame,
    beta: pd.Series | pd.DataFrame | None = None,
    sector_map: dict[str, str] | None = None,
) -> dict[str, pd.Series | pd.DataFrame]:
    """Build exposure diagnostics used by reports."""

    report: dict[str, pd.Series | pd.DataFrame] = {
        "gross_exposure": gross_exposure(weights),
        "net_exposure": net_exposure(weights),
        "concentration": concentration(weights),
    }
    if beta is not None:
        report["beta_exposure"] = beta_exposure(weights, beta)
    if sector_map is not None:
        report["sector_exposure"] = sector_exposure(weights, sector_map)
    return report

