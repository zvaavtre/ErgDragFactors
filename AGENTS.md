# AGENTS.md

## Attribution & Source

The original research synthesis in this repository was generated and compiled by **Gemini 4 Argon** (via Google Antigravity). With **Claude** sanity checking everything as best it could.

## Repository Context for Agents

When working in or extending `ErgDragFactors`, keep the following conventions and domain principles in mind:

1. **Hard Engineering & Citation Requirements:**
   - **ALWAYS Use Libraries Rather Than Rolling Custom Code:** For all common tasks—such as statistical tests, correlations, regressions, p-values, numerical integration, HTML/DOM parsing, data manipulation, charting, and unit testing—**always use established, battle-tested libraries** (e.g., `scipy`, `numpy`, `pandas`, `beautifulsoup4`, `matplotlib`, `pytest` / `unittest`) rather than writing custom implementations from scratch. Save custom code strictly for domain-specific rowing physics and logic that standard libraries do not provide.
   - **ALWAYS Verify Sources Are Real & Exact:** Never cite a paper, book, newsletter, or URL from memory. Open the source and confirm the exact title, authors, year, journal, volume/pages, ISBN, PMID/DOI, URL, and the claim itself. If you can only reach an abstract, excerpt, or secondary report, ask the user to download the source into `references/` so you can read it. After reading it, add its citation and a working link to [`docs/references.md`](docs/references.md), then delete the download. If the user cannot get the source, record what was read in [`docs/references.md`](docs/references.md).
   - **No Unsourced Recommendations:** Every drag factor number and every recommendation about behaviour must come from a publication listed in [`docs/references.md`](docs/references.md). Do not invent numbers, adjustments, or advice, and do not derive advice from our own models. If no source says it, say so.
   - **Keep the Docs Short:** State the recommendation and its source. Do not add narrative prose.
   - **Keep the Tone Neutral:** State facts and reasons. Do not add snark or complaints about effort, size, or cost.
   - **Mathematical & Data Integrity Tests:** Any change to the archived Python in `data/` must keep `data/test_math.py` passing (`make test` in `data/Makefile`).

2. **Core Domain Focus:**
   - **Drag Factor vs. Damper Setting (1–10):** Always model and reference the PM5 **Drag Factor** ($k$, where $\tau_{\text{drag}} = k\omega^2$), not raw damper numbers. Damper guidance may be quoted only as the source published it.
   - **Starting Points:** Present drag factor numbers as starting points, never as optima. Published recommendations are by sex, weight and age. Do not publish a drag factor by height unless a verified source gives one.
   - **Race Data:** C.R.A.S.H.-B. data has no drag factor or drive length, so never use it to support or reject a drag factor recommendation. Call its heights name-matched, not verified. Do not fabricate heights for unmatched rowers.

3. **Archived Pipeline, Privacy & Git Hygiene Constraints (`data/`):**
   - **Archived Code:** [`data/`](data/) is kept as a record and is not used by the main docs. [`data/README.md`](data/README.md) explains why. Do not cite its results as support for any recommendation.
   - **No Raw Downloads or Outputs in Git:** Raw downloads, CSVs, charts, and the generated report are excluded via [`.gitignore`](.gitignore). Only scripts, the Makefile, and the README belong in version control.
   - **Athlete Pseudonymization (No Raw PII/Names):** Never capture, store, or output individual rowers' names or roster affiliation strings in any CSV, script, or documentation file. When joining individual athletes across datasets (e.g., matching public heights) is required, use a **pseudonymous hash** (`athlete_id = sha256("ergdrag:" + normalized_name)[:12]`) and describe the dataset accurately as **pseudonymized** (since public race times and event codes are inherently linkable to public regatta results).

4. **Project Structure:**
   - [`README.md`](README.md) — Whether height-based drag factors have data behind them, how to set your drag factor, published starting points, and sourced recommendations.
   - [`docs/references.md`](docs/references.md) — Verified sources and what each one says.
   - [`data/`](data/README.md) — Archived race data pipeline, with a README explaining why it is not used (`data/raw/` and all outputs are excluded from Git).
   - [`DECISIONS.md`](DECISIONS.md) — Log of human design choices, domain corrections, and the full audit of the original content.
