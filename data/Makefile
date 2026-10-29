# Makefile for C.R.A.S.H.-B. & WRIC Ergometer Data Pipeline
# Raw HTML/telemetry caches in data/raw/ are git-ignored; only summary CSVs are tracked.

PYTHON ?= uv run --python 3.12

SUMMARY_CSVS = \
	athlete_heights.csv \
	crashb_2k_summary.csv \
	crashb_quarter_telemetry.csv \
	eval_height_vs_rate_summary.csv \
	eval_category_summary.csv \
	eval_telemetry_pacing_summary.csv

.PHONY: all heights fetch evaluate test clean-raw clean help

all: heights fetch evaluate test

heights:
	$(PYTHON) build_athlete_heights.py

athlete_heights.csv: build_athlete_heights.py
	$(PYTHON) build_athlete_heights.py

fetch: athlete_heights.csv
	$(PYTHON) fetch_crashb.py

crashb_2k_summary.csv: athlete_heights.csv fetch_crashb.py
	$(PYTHON) fetch_crashb.py

evaluate: crashb_2k_summary.csv athlete_heights.csv
	$(PYTHON) evaluate_crashb.py

test: crashb_2k_summary.csv athlete_heights.csv
	$(PYTHON) test_math.py

clean-raw:
	rm -rf raw/

clean: clean-raw
	rm -f athlete_heights.csv crashb_2k_summary.csv crashb_quarter_telemetry.csv \
	      eval_height_vs_rate_summary.csv eval_category_summary.csv \
	      eval_telemetry_pacing_summary.csv
	rm -rf charts/

help:
	@echo "Available targets:"
	@echo "  make all        - Build heights, parse CRASH-B/WRIC data, evaluate, and run tests"
	@echo "  make heights    - Run build_athlete_heights.py (rebuilds pseudonymized athlete_heights.csv)"
	@echo "  make fetch      - Run fetch_crashb.py (builds pseudonymized summary CSVs from Time-Team)"
	@echo "  make evaluate   - Run evaluate_crashb.py (builds evaluation CSVs, charts, and docs/04 report)"
	@echo "  make test       - Run test_math.py (verifies physics, regressions, and dataset invariants)"
	@echo "  make clean-raw  - Remove git-ignored raw HTML cache (data/raw/)"
	@echo "  make clean      - Remove raw cache and generated summary CSVs/charts"
