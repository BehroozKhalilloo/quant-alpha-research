# Interviewer Summary

## One-Minute Version

This project is a reproducible cross-sectional equity alpha research stack. It studies liquidity-adjusted reversal using public daily data, then evaluates the signal with shifted features, train/test and purged walk-forward validation, Newey-West inference, false-discovery checks, transaction costs, capacity, risk diagnostics, and a professional research memo.

## What The Candidate Is Demonstrating

- Economic hypothesis formation rather than a black-box backtest.
- Awareness of yfinance and static-universe limitations.
- Modular Python research engineering.
- Statistical discipline: IC, rank IC, Newey-West, bootstrap, FDR, walk-forward.
- Portfolio realism: dollar neutrality, turnover, costs, capacity, exposure checks.
- Trading intuition via a Kelly sizing scenario module.

## What The Results Do And Do Not Prove

The included multi-sleeve blend has attractive sample metrics and beats weaker baselines. It does not prove institutional alpha because the data is not point-in-time, delisting-aware, or borrow-aware. The project is best read as evidence of research taste and engineering ability, not as a live trading claim.

## Fast Review Path

1. Read `reports/research_memo.md`.
2. Inspect `reports/generated_report.md`.
3. Run `make test`.
4. Review `src/quant_alpha/signal.py`, `portfolio.py`, `backtest.py`, `stats.py`, and `costs.py`.
5. Check `docs/reproducibility_checklist.md` and `docs/data_dictionary.md`.

