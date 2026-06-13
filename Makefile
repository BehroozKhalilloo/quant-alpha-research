.PHONY: install test data research backtest report

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

report:
	python scripts/generate_report.py

