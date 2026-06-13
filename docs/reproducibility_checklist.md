# Reproducibility Checklist

- Use Python 3.11 or newer.
- Install with `make install`.
- Run `make all` from the repository root.
- Confirm `pytest` passes.
- Confirm `reports/generated_report.md` is regenerated locally.
- Record config changes in `config/default.yaml`.
- Do not compare strategy variants without noting whether they were exploratory or pre-specified.
- Do not treat yfinance results as point-in-time institutional evidence.
- Replace the default universe with point-in-time membership before making institutional claims.
- Review transaction-cost and capacity tables before interpreting cumulative returns.

