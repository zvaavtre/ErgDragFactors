# Makefile for C.R.A.S.H.-B. & WRIC Ergometer Data Pipeline
# Raw HTML/telemetry caches in data/raw/ are git-ignored; only summary CSVs are tracked.

PYTHON ?= python3

SUMMARY_CSVS = \
	crashb_2k_summary.csv \
	crashb_quarter_telemetry.csv \
	eval_height_vs_rate_summary.csv \
	eval_category_summary.csv \
	eval_telemetry_pacing_summary.csv

.PHONY: all fetch evaluate clean-raw clean help

all: fetch evaluate

fetch:
	$(PYTHON) fetch_crashb.py

evaluate: crashb_2k_summary.csv athlete_heights.csv
	$(PYTHON) evaluate_crashb.py

crashb_2k_summary.csv:
	$(PYTHON) fetch_crashb.py

clean-raw:
	rm -rf raw/

clean: clean-raw
	rm -f crashb_2k_summary.csv crashb_quarter_telemetry.csv \
	      eval_height_vs_rate_summary.csv eval_category_summary.csv \
	      eval_telemetry_pacing_summary.csv
	rm -rf charts/

help:
	@echo "Available targets:"
	@echo "  make all        - Download/parse CRASH-B & WRIC data and run statistical evaluation"
	@echo "  make fetch      - Run fetch_crashb.py (builds anonymized summary CSVs from Time-Team)"
	@echo "  make evaluate   - Run evaluate_crashb.py (builds evaluation CSVs and docs/04 report)"
	@echo "  make clean-raw  - Remove git-ignored raw HTML cache (data/raw/)"
	@echo "  make clean      - Remove raw cache and generated summary CSVs (preserves athlete_heights.csv)"
