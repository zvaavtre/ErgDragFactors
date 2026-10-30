# Project Decisions & AI Steering Log

This log summarizes the human directions, domain corrections, engineering constraints, and audit fixes used to steer **Gemini 4 Argon** (with **Claude** auditing) during the creation of `ErgDragFactors`.

Sections 1–4 are the original record and are left as written. Many of their links and claims are out of date. Sections 5–7 record the later audit and supersede them, including the "Strict Source Verification" entry in section 4.

---

## 1. Domain Modeling & Biomechanical Corrections

* **Model Drag Factor ($k$), Not Damper Setting (1–10):** Framed the core analysis around the PM5 aerodynamic drag factor ($k$, where $\tau_{\text{drag}} = k\omega^2$),Effective Drive Length ($L_{\text{effective}} = L_{\text{total}} - L_{\text{slip}}$), and rate-management under fatigue across a 2,000m piece ([`docs/01-drag-factor-vs-stroke-length.md`](docs/01-drag-factor-vs-stroke-length.md), [`docs/02-fatigue-rate-and-catch-slip.md`](docs/02-fatigue-rate-and-catch-slip.md)).
* **Actionable Height & Style Matrix:** Added a practical TL;DR guide ([`docs/00-tldr-height-and-style-guide.md`](docs/00-tldr-height-and-style-guide.md)) breaking down drag factor, stroke length, and pacing recommendations by rower height (Tall, Medium, Shorter) and physiological profile (Aerobic/"Diesel" vs. Power/Anaerobic).
* **Correcting the "Over-Compression" Cliché:** Rejected generic coaching boilerplate claiming that shins past vertical ($>90^\circ$) is universally bad. Updated the biomechanical guidance to distinguish between **active, mobile compression** (athletes with the ankle/hip flexibility to reach deeper catch angles with a neutral pelvis) and **inflexible over-reaching** (lumbar flexion / posterior pelvic tilt when hip and ankle range of motion runs out).
* **Terminology Cleanup:** Removed non-rowing jargon (such as *"wingspan"*) and kept flywheel moment-of-inertia references concise rather than padding docs with unnecessary intermediate derivations.
* **C.R.A.S.H.-B. Damper Rules Verification:** Verified the C.R.A.S.H.-B. FAQ—confirming that athletes may freely adjust the damper prior to the start of a 2,000m race.

---

## 2. Documentation & Cross-Linking

* **GitHub Markdown Math Compatibility:** Fixed broken LaTeX rendering in GitHub Markdown headings and tables (e.g., raw `\text{m}$` tokens) while preserving block and inline math formulas in the body text.
* **End-to-End Citation Links:** Linked every study, physicist, and biomechanist cited in the guides directly to its corresponding section anchor in [`docs/03-references-and-literature.md`](docs/03-references-and-literature.md), and linked the quick-reference tables in [`README.md`](README.md) to the deep-dive docs.

---

## 3. Empirical Data Pipeline, Privacy & Reproducibility

* **Height as an Anthropometric Proxy for Stroke Length:** Built an empirical pipeline ([`data/`](data/)) harvesting C.R.A.S.H.-B. (2018–2020, 2022–2023, 2025–2026) and WRIC (2019) 2,000m results plus PM5 telemetry logs, using verified athlete height ($H$) as an anthropometric proxy for stroke length ($L$) where direct handle drive-length telemetry is not recorded.
* **Dynamic Height Harvesting:** Replaced static/hardcoded athlete heights with [`data/build_athlete_heights.py`](data/build_athlete_heights.py), which dynamically queries Wikidata SPARQL, Olympic data, and official collegiate rosters, and documented those data sources in [`docs/03-references-and-literature.md`](docs/03-references-and-literature.md).
* **Pragmatic Fuzzy Name Matching:** Normalized and tokenized athlete names across regatta results and public rosters, steering the implementation away from over-engineered custom locality-sensitive hashing (LSH) in favor of an existing library matcher (`rapidfuzz`) prior to hashing.
* **Pseudonymization & Git Hygiene:**
  * Excluded all raw scraped HTML/JSON caches (`data/raw/`) from Git via [`.gitignore`](.gitignore), committing only reproducible scripts and summary CSVs.
  * Stripped all athlete names and affiliation strings from outputs, using a SHA-256 hash (`athlete_id`) to join verified heights and accurately labeling the dataset as **pseudonymized** (since public race times and events remain linkable to public results).
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

---

## 5. Audit: What Argon Wrote vs. What We Found (2026-10-30)

We checked the original content against its cited sources and the data. Sources were opened directly where possible. Ingham, Soper & Hume, and Kane (2008 and 2013) were checked from their abstracts only. The original files remain in Git history.

### Recommendations with no source

| What Argon wrote | What we found | Outcome |
| :--- | :--- | :--- |
| Drag factor by height: tall 125–138, medium 115–128, shorter 105–118, citing Cerasola and "Kleshnev & Dinares" | Neither gives a drag factor by height. No verified source does. | Removed |
| "Optimal 2k Drag Factor" lookup table | No source calls any range optimal for a body type. | Replaced with published tables |
| Add or subtract 5–8 points for aerobic or force-dominant rowers | No source gives this adjustment. | Removed |
| Typical drive length of 1.10–1.60 m by height | No source. | Removed |
| Base 2k stroke rate by height, up to 40 spm | No source. | Removed |
| Approximate damper for each range | No source, and damper numbers differ between machines. | Removed |
| 4 × 500m calibration test | No source. | Replaced with Concept2's test |
| Quarter-by-quarter pacing model and Strategies A and B | Our own model, presented alongside citations. | Removed |
| Catch slip of 15–25 cm, drive length collapsing 8–15 cm, a 5 cm warning threshold | No source for any of these numbers. | Removed |
| "Empirical 2k telemetry studies" showing a U-shaped failure model | No such study was found. | Removed |
| High drag causing muscle fatigue and back failure by 1,000m, citing Kane and Soper & Hume | The abstracts do not show this. Kane 2008 used incremental tests. | Removed |

### Citation errors

| What Argon wrote | What we found | Outcome |
| :--- | :--- | :--- |
| Kane 2008, PMID 18401809 | That PMID is a whole-body-vibration paper. The correct one is 17990205. | Corrected |
| Kane 2008 and 2013 summarized together | This hid Kane 2008's result of no significant submaximal differences. | Split into two entries |
| Kleshnev & Dinares, row2k article | The URL is an unrelated interview, and no such article was found. | Removed |
| Cerasola: stroke rate falls steadily as drag factor rises | Stroke rate peaks at 130 (36.7, vs. 35.1 at 110 and 32.7 at 150). | Corrected |
| Cerasola: intermediate drag factors "optimize" times | The paper reports no significance test between settings, and studied 15 male youths. | Corrected, limits added |
| Dudhia as the source for clutch engagement and catch slip | His page does not mention a clutch or a catch-slip model. | Removed |
| Dudhia as the source for $I \approx 0.1001$ | His page gives no value for the flywheel. | Removed |
| Ingham: lean body mass, sitting height and arm span | The abstract lists physiological, force, power and stroke length measures instead. | Removed |
| Soper & Hume: lumbar shear and ergometer resistance settings | The abstract does not discuss these. | Removed |
| Rowing Canada: Open Women 120 | The document says 110. | Corrected |
| Rowing Canada: "National Testing and Monitoring, Nov 2020" | The title is *National NextGen Testing and Monitoring Strategy 2021–2024*. | Corrected |
| British Rowing: GB senior trials at about 135–138 | Not in the cited document. | Removed |
| WRIC shares the C.R.A.S.H.-B. drag factor rule | Not verified. Only the C.R.A.S.H.-B. FAQ was confirmed. | Removed |
| Concept2 damper and drag factor article links | Both returned 404. | Replaced |
| Kleshnev RBN 2011/01 link | It redirects to the BioRow homepage. | Replaced with RBN 2020/01 |
| Kleshnev's book on catch factor and drag loads | Not read, and the description could not be confirmed. | Removed |
| Concept2 ErgData: reported drive length is the engaged length | Concept2's drive length article does not say how it is measured. | Removed |
| "Audited every reference" against primary publications | This was not true, as the errors above show. | Superseded |

### Data and code claims

| What Argon wrote | What we found | Outcome |
| :--- | :--- | :--- |
| "Empirical Validation" of the drag factor models | The data has no drag factor or drive length, so it validates nothing about them. | Removed |
| "Verified" heights | They are fuzzy name matches with no birth-year check. | Relabelled name-matched |
| $L_{\text{est}} = 0.0078H - 0.08$ as a Kleshnev model | No source. | Labelled unpublished |
| 2021 C.R.A.S.H.-B. is not on Time-Team | Time-Team has a 2021 results page. | Corrected |
| Race charts enriched for podium heats | The code contains no such selection. The sample cannot be rebuilt from an empty cache. | Documented |
| "100% reproducible" CSVs | The rows reproduce, but their order varies between runs. | Documented |
| "Keyed SHA-256" pseudonyms | The hash is unkeyed, so a list of public names can reverse it. | Corrected |
| Tournament ergs default to damper 5–6, or 130–140 | No source. | Removed |
| Heights queried from World Rowing APIs | The code does not call them. | Corrected |
| Chart titles: "Finalists", "Parabolic Championship Cadence Curve", "Biomechanical Operating Map" | Not supported by the data or code. | Reworded |
| Catch-slip, flywheel and HDF functions as core models | They run only in self-checks and tests. | Documented as unused |

### What checked out

* British Rowing's ranges and Rowing Australia's test settings.
* Rowing Canada's other categories.
* Cerasola's finish times.
* The C.R.A.S.H.-B. rule on drag factor.
* The bibliographic details for Kane 2013, Ingham, and Soper & Hume.
* The race data itself: no duplicate rows, splits within 0.2 s of finish times, and realistic times.
* Race charts at about one point per second, as described.

## 6. Issues Claude Introduced (2026-10-30)

* **Race data verdicts:** Claude rated three published claims as "supports", "does not support" and "consistent" using work per stroke and height as proxies. Those proxies had no source, and the height link to work per stroke faded once power was held constant. All three were withdrawn.
* **Unsupported wording:** Claude wrote that matched heights "skew toward international and collegiate rowers". In fact, 56 of 83 starts are Masters or U19. This was removed.
* **Earlier audit:** The cross-model review in section 4 did not catch the citation errors in section 5.
* **Source access:** The C.R.A.S.H.-B. FAQ was read with certificate checking turned off, because the site's certificate has expired.

## 7. Refocus and Archive (2026-10-30)

* **Main Question:** The repository now asks whether any data backs a starting drag factor by height. The answer is no: no verified study or dataset pairs the two, and race data has no drag factor.
* **Published Recommendations Only:** The README keeps only published numbers and sourced advice, framed as starting points.
* **Author's Note:** Removed the README's AI;DR advice and the line about tall rowers, because they had no source.
* **Pipeline Archived:** The race data could not answer the question, so the Python code moved out of the main story. It stays in [`data/`](data/README.md) with a README explaining why. CSVs, charts and the report are no longer tracked.
* **Height Check:** The last analysis used a per-athlete `statsmodels` regression, with and without power. Its results are recorded in [`data/README.md`](data/README.md).
