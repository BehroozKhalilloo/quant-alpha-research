.PHONY: install test data research backtest robustness diagnostics trader report all

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

trader:
	python scripts/run_trader_extension.py

report:
	python scripts/generate_report.py

all: data research backtest robustness diagnostics trader report test
