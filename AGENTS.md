# AGENTS.md

## Attribution & Source

The research synthesis, mathematical derivations, biomechanical models, and pacing documentation in this repository were generated and compiled by **Gemini 4 Argon** (via Google Antigravity).

## Repository Context for Agents

When working in or extending `ErgDragFactors`, keep the following conventions and domain principles in mind:

1. **Hard Engineering & Citation Requirements:**
   - **ALWAYS Use Libraries Rather Than Rolling Custom Code:** For all common tasks—such as statistical tests, correlations, regressions, p-values, numerical integration, HTML/DOM parsing, data manipulation, charting, and unit testing—**always use established, battle-tested libraries** (e.g., `scipy`, `numpy`, `pandas`, `beautifulsoup4`, `matplotlib`, `pytest` / `unittest`) rather than writing custom implementations from scratch. Save custom code strictly for domain-specific rowing physics and logic that standard libraries do not provide.
   - **ALWAYS Verify Sources Are Real & Exact:** Never cite a paper, book, newsletter, or URL from memory without verifying that the exact title, authors, publication year, journal, volume/pages, ISBN, PMID/DOI, and URL actually exist and are not conflated across different works.
   - **Mathematical & Data Integrity Tests:** All Python scripts and domain calculations in `data/` must be covered by automated tests (`data/test_math.py`, runnable via `make test` in `data/Makefile`) that verify the math, statistical outputs, and dataset invariants (e.g., ensuring every configured regatta year parses > 0 records and every derived column matches its defining formula).

2. **Core Domain Focus:**
   - **Drag Factor vs. Damper Setting (1–10):** Always model and reference the PM5 **Drag Factor** ($k$, where $\tau_{\text{drag}} = k\omega^2$), never raw damper numbers, except as approximate clean-cage translations.
   - **Effective Drive Length & Catch Slip:** Distinguish between total physical reach ($L_{\text{total}}$), catch slip ($L_{\text{slip}}$), and engaged flywheel travel ($L_{\text{effective}} = L_{\text{total}} - L_{\text{slip}}$).
   - **Height as Proxy for Stroke Length:** When empirical datasets lack direct handle drive-length ($L$) telemetry, use verified rower **height ($H$)** (and structural weight/age classes) as an anthropometric proxy for stroke length ($L_{\text{est}} \approx 0.0078 \cdot H_{\text{cm}} - 0.08\text{ m}$). Do not fabricate individual heights from category lookup tables when an athlete's height is unverified, and explicitly state when empirical datasets lack direct PM5 drag-factor ($k$) or drive-length ($L$) logs.
   - **Primary Literature:** Ground any additions or calculators in the work of [**Anu Dudhia**](docs/03-references-and-literature.md#anu-dudhia-oxford-the-physics-of-rowing) (Oxford University flywheel physics) and [**Dr. Valery Kleshnev**](docs/03-references-and-literature.md#valery-kleshnev-biorow-handle-drag-factor) (BioRow Handle Drag Factor $\text{HDF}$ and catch-slip telemetry).

3. **Data Pipeline, Privacy & Git Hygiene Constraints (`data/`):**
   - **Location & Reproducibility:** All datasets, roster height builders ([`data/build_athlete_heights.py`](data/build_athlete_heights.py)), harvesting scripts ([`data/fetch_crashb.py`](data/fetch_crashb.py)), statistical evaluation scripts ([`data/evaluate_crashb.py`](data/evaluate_crashb.py)), test suites ([`data/test_math.py`](data/test_math.py)), and the [`data/Makefile`](data/Makefile) must live inside the [`data/`](data/) folder. Every CSV and chart in `data/` must be 100% reproducible via [`data/Makefile`](data/Makefile).
   - **No Raw Downloads in Git:** Raw downloaded files (HTML pages, JSON race charts, scrape caches in `data/raw/`) **do not belong in Git** and must remain excluded via [`.gitignore`](.gitignore). Only cleaned, aggregated **summary CSVs** (`data/*.csv`) and scripts belong in version control.
   - **Athlete Pseudonymization (No Raw PII/Names):** Never capture, store, or output individual rowers' names or roster affiliation strings in any CSV, script, or documentation file. When joining individual athletes across datasets (e.g., matching verified heights) is required, use a **pseudonymous hash** (`athlete_id = sha256("ergdrag:" + normalized_name)[:12]`) and describe the dataset accurately as **pseudonymized** (since public race times and event codes are inherently linkable to public regatta results).

4. **Project Structure:**
   - [`README.md`](README.md) — Overview, lookup tables, and core equations.
   - [`docs/00-tldr-height-and-style-guide.md`](docs/00-tldr-height-and-style-guide.md) — Actionable TL;DR guide broken out by rower height and physiological style.
   - [`docs/01-drag-factor-vs-stroke-length.md`](docs/01-drag-factor-vs-stroke-length.md) — Mechanical & biomechanical models for Drag Factor vs. Drive Length in a 2,000m test.
   - [`docs/02-fatigue-rate-and-catch-slip.md`](docs/02-fatigue-rate-and-catch-slip.md) — Rate ($R$) vs. Catch Slip ($L_{\text{slip}}$) optimization under fatigue across 2k quarters.
   - [`docs/03-references-and-literature.md`](docs/03-references-and-literature.md) — Verified primary academic, physics, and manufacturer references.
   - [`docs/04-crash-b-empirical-analysis.md`](docs/04-crash-b-empirical-analysis.md) — Empirical analysis of C.R.A.S.H.-B. (2018–2020, 2022–2023, 2025–2026) & WRIC (2019) 2,000m results and PM5 telemetry.
   - [`data/`](data/) — Pseudonymized summary CSVs, harvester/evaluation/test scripts, and [`Makefile`](data/Makefile) (`data/raw/` is excluded from Git).
