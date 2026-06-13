.PHONY: install test data research backtest robustness diagnostics report all

install:
	python -m pip install -e ".[dev]"

test:
	pytest

data:
	python scripts/download_data.py

research:
	python scripts/run_research.py

backtest:
	python scripts/run_backtest.py

robustness:
	python scripts/run_robustness.py

diagnostics:
	python scripts/run_diagnostics.py

report:
	python scripts/generate_report.py

all: data research backtest robustness diagnostics report test
