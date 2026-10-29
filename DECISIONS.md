# Project Decisions & AI Steering Log

This log summarizes the human directions, domain corrections, engineering constraints, and audit fixes used to steer **Gemini 4 Argon** (with **Claude** auditing) during the creation of `ErgDragFactors`.

---

## 1. Domain Modeling & Biomechanical Corrections

* **Model Drag Factor ($k$), Not Damper Setting (1–10):** Framed the core analysis around the PM5 aerodynamic drag factor ($k$, where $\tau_{\text{drag}} = k\omega^2$),Effective Drive Length ($L_{\text{effective}} = L_{\text{total}} - L_{\text{slip}}$), and rate-management under fatigue across a 2,000m piece ([`docs/01-drag-factor-vs-stroke-length.md`](docs/01-drag-factor-vs-stroke-length.md), [`docs/02-fatigue-rate-and-catch-slip.md`](docs/02-fatigue-rate-and-catch-slip.md)).
* **Actionable Height & Style Matrix:** Added a practical TL;DR guide ([`docs/00-tldr-height-and-style-guide.md`](docs/00-tldr-height-and-style-guide.md)) breaking down drag factor, stroke length, and pacing recommendations by rower height (Tall, Medium, Shorter) and physiological profile (Aerobic/"Diesel" vs. Power/Anaerobic).
* **Correcting the "Over-Compression" Cliché:** Rejected generic coaching boilerplate claiming that shins past vertical ($>90^\circ$) is universally bad. Updated the biomechanical guidance to distinguish between **active, mobile compression** (athletes with the ankle/hip flexibility to reach deeper catch angles with a neutral pelvis) and **inflexible over-reaching** (lumbar flexion / posterior pelvic tilt when hip and ankle range of motion runs out).
* **Terminology Cleanup:** Removed non-rowing jargon (such as *"wingspan"*) and kept flywheel moment-of-inertia references concise rather than padding docs with unnecessary intermediate derivations.
* **C.R.A.S.H.-B. Damper Rules Verification:** Verified official C.R.A.S.H.-B. and World Rowing Indoor Championship rules—confirming that athletes may freely adjust the damper prior to the start of a 2,000m race (while noting that unmodified tournament ergs typically default to damper 5–6, or ~130–140 drag factor on brand-new cages).

---

## 2. Documentation & Cross-Linking

* **GitHub Markdown Math Compatibility:** Fixed broken LaTeX rendering in GitHub Markdown headings and tables (e.g., raw `\text{m}$` tokens) while preserving block and inline math formulas in the body text.
* **End-to-End Citation Links:** Linked every study, physicist, and biomechanist cited in the guides directly to its corresponding section anchor in [`docs/03-references-and-literature.md`](docs/03-references-and-literature.md), and linked the quick-reference tables in [`README.md`](README.md) to the deep-dive docs.

---

## 3. Empirical Data Pipeline, Privacy & Reproducibility

* **Height as an Anthropometric Proxy for Stroke Length:** Built an empirical pipeline ([`data/`](data/)) harvesting C.R.A.S.H.-B. (2018–2020, 2022–2023, 2025–2026) and WRIC (2019) 2,000m results plus PM5 telemetry logs, using verified athlete height ($H$) as an anthropometric proxy for stroke length ($L$) where direct handle drive-length telemetry is not recorded.
* **Dynamic Height Harvesting:** Replaced static/hardcoded athlete heights with [`data/build_athlete_heights.py`](data/build_athlete_heights.py), which dynamically queries Wikidata SPARQL, World Rowing athlete APIs, and official collegiate rosters, and documented those data sources in [`docs/03-references-and-literature.md`](docs/03-references-and-literature.md).
* **Pragmatic Fuzzy Name Matching:** Normalized and tokenized athlete names across regatta results and public rosters, steering the implementation away from over-engineered custom locality-sensitive hashing (LSH) in favor of an existing library matcher (`rapidfuzz`) prior to hashing.
* **Pseudonymization & Git Hygiene:**
  * Excluded all raw scraped HTML/JSON caches (`data/raw/`) from Git via [`.gitignore`](.gitignore), committing only reproducible scripts and summary CSVs.
  * Stripped all athlete names and affiliation strings from outputs, using a one-way SHA-256 hash (`athlete_id`) to join verified heights and accurately labeling the dataset as **pseudonymized** (since public race times and events remain linkable to public results).
* **Single-Command Reproducibility & Automated Charts:** Required all data harvesting, height matching, statistical evaluation, and SVG chart generation to run end-to-end via [`data/Makefile`](data/Makefile).

---

## 4. Verification, Testing & Audit Fixes

* **Hard Requirement — Use Established Libraries:** Mandated in [`AGENTS.md`](AGENTS.md) that all standard operations—statistics, regressions, HTML parsing, fuzzy matching, charting, and testing—use battle-tested libraries (`scipy`, `numpy`, `pandas`, `beautifulsoup4`, `matplotlib`, `rapidfuzz`, `pytest`) rather than custom code.
* **Strict Source Verification:** Audited every reference in [`docs/03-references-and-literature.md`](docs/03-references-and-literature.md) against primary publications (PubMed, DOI, ISBN, Oxford Physics, Concept2, BioRow) to eliminate hallucinated or conflated citations.
* **Mathematical & Dataset Invariant Tests:** Added [`data/test_math.py`](data/test_math.py) (`make test`) to verify physics equations, statistical outputs, and pipeline invariants (such as asserting every configured regatta year parses $>0$ rows).
* **Claude Audit Remediation:** Addressed six issues flagged during cross-model review:
  1. **Strategy B Deceleration Math:** Corrected the recovery deceleration calculation in [`docs/02-fatigue-rate-and-catch-slip.md`](docs/02-fatigue-rate-and-catch-slip.md) ($\dot{\omega} = -(k/I)\omega^2 \approx -28\text{ rad/s}^2$, yielding a ~2–3 rad/s extra slowdown and ~3–5% slip reduction when dropping from 34 to 32 spm at constant power, rather than 19%).
  2. **2022 C.R.A.S.H.-B. Parser Bug:** Fixed [`data/fetch_crashb.py`](data/fetch_crashb.py) to dynamically map table headers so the extra `Category` column and letter age codes (`M A`–`M K`) in the 2022 results table parse all 368 rows instead of silently dropping them.
  3. **No Hardcoded Prose Claims:** Removed hardcoded summary numbers in [`data/evaluate_crashb.py`](data/evaluate_crashb.py) and updated [`docs/04-crash-b-empirical-analysis.md`](docs/04-crash-b-empirical-analysis.md) so all reported correlations, averages, and $p$-values match computed dataset outputs.
  4. **Removed Fabricated Category Heights:** Dropped synthetic category-average height lookups (`CATEGORY_HEIGHT_CM`) for unverified rowers, restricting height regressions strictly to verified-height athletes and controlling for heavyweight vs. lightweight confounding.
  5. **Non-Circular Pacing Analysis:** Reframed the Q3 split-decay analysis in [`docs/04-crash-b-empirical-analysis.md`](docs/04-crash-b-empirical-analysis.md) as a descriptive comparison of pacing profiles rather than a circular causal claim.
  6. **Scope Transparency:** Explicitly documented dataset limitations (lack of direct PM5 drag-factor logs in public race tables and fast-finisher selection bias in the 400 telemetry charts).
