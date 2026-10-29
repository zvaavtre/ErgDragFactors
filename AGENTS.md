# AGENTS.md

## Attribution & Source

The research synthesis, mathematical derivations, biomechanical models, and pacing documentation in this repository were generated and compiled by **Gemini 4 Argon** (via Google Antigravity).

## Repository Context for Agents

When working in or extending `ErgDragFactors`, keep the following conventions and domain principles in mind:

1. **Core Domain Focus:**
   - **Drag Factor vs. Damper Setting (1–10):** Always model and reference the PM5 **Drag Factor** ($k$, where $\tau_{\text{drag}} = k\omega^2$), never raw damper numbers, except as approximate clean-cage translations.
   - **Effective Drive Length & Catch Slip:** Distinguish between total physical reach ($L_{\text{total}}$), catch slip ($L_{\text{slip}}$), and engaged flywheel travel ($L_{\text{effective}} = L_{\text{total}} - L_{\text{slip}}$).
   - **Height as Proxy for Stroke Length:** When empirical datasets lack direct handle drive-length ($L$) telemetry, use rower **height ($H$)** (and structural stature/weight classes) as the primary anthropometric proxy for stroke length ($L_{\text{est}} \approx 0.0078 \cdot H_{\text{cm}} - 0.08\text{ m}$).
   - **Primary Literature:** Ground any additions or calculators in the work of [**Anu Dudhia**](docs/03-references-and-literature.md#anu-dudhia-oxford-the-physics-of-rowing) (Oxford University flywheel physics) and [**Dr. Valery Kleshnev**](docs/03-references-and-literature.md#valery-kleshnev-biorow-handle-drag-factor) (BioRow Handle Drag Factor $\text{HDF}$ and catch-slip telemetry).

2. **Data Pipeline, Privacy & Git Hygiene Constraints (`data/`):**
   - **Location & Reproducibility:** All datasets, harvesting scripts ([`data/fetch_crashb.py`](data/fetch_crashb.py)), statistical evaluation scripts ([`data/evaluate_crashb.py`](data/evaluate_crashb.py)), and the [`data/Makefile`](data/Makefile) must live inside the [`data/`](data/) folder. Any new data collection or evaluation step must be runnable via [`data/Makefile`](data/Makefile).
   - **No Raw Downloads in Git:** Raw downloaded files (HTML pages, JSON race charts, scrape caches in `data/raw/`) **do not belong in Git** and must remain excluded via [`.gitignore`](.gitignore). Only cleaned, aggregated **summary CSVs** (`data/*.csv`) and evaluation scripts belong in version control.
   - **Strict Athlete Anonymization (No PII/Names):** Never capture, store, or output individual rowers' names in any CSV, script, or documentation file. If tracking or joining individual athletes across datasets (e.g., matching roster heights) is required, immediately apply a **one-way cryptographic hash** (`athlete_id = sha256("ergdrag:" + normalized_name)[:12]`) and discard the name. If individual tracking is not needed, omit identifiers entirely.

3. **Project Structure:**
   - [`README.md`](README.md) — Overview, lookup tables, and core equations.
   - [`docs/00-tldr-height-and-style-guide.md`](docs/00-tldr-height-and-style-guide.md) — Actionable TL;DR guide broken out by rower height and physiological style.
   - [`docs/01-drag-factor-vs-stroke-length.md`](docs/01-drag-factor-vs-stroke-length.md) — Mechanical & biomechanical models for Drag Factor vs. Drive Length in a 2,000m test.
   - [`docs/02-fatigue-rate-and-catch-slip.md`](docs/02-fatigue-rate-and-catch-slip.md) — Rate ($R$) vs. Catch Slip ($L_{\text{slip}}$) optimization under fatigue across 2k quarters.
   - [`docs/03-references-and-literature.md`](docs/03-references-and-literature.md) — Primary academic, physics, and manufacturer references.
   - [`docs/04-crash-b-empirical-analysis.md`](docs/04-crash-b-empirical-analysis.md) — Empirical analysis of 2018–2026 C.R.A.S.H.-B. & WRIC 2,000m results and PM5 telemetry.
   - [`data/`](data/) — Anonymized summary CSVs, harvester/evaluation scripts, and [`Makefile`](data/Makefile) (`data/raw/` is excluded from Git).
