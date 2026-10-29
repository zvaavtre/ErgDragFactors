# Empirical Analysis: C.R.A.S.H.-B. & World Indoor Championship Data (2018–2026)

This document summarizes the empirical findings from **4,620 individual 2,000m championship race records** and **400 1 Hz PM5 race-chart telemetry logs** harvested from the **C.R.A.S.H.-B. Sprints (2018, 2019, 2020, 2022, 2023, 2025, 2026)** and the **World Rowing Indoor Championships (WRIC 2019)**.

*(Note: The 2021 and 2024 C.R.A.S.H.-B. editions are not hosted on the Time-Team regatta server and are not included in this dataset.)*

---

## 1. Scope, Methodological Limitations & Dataset Architecture

> [!IMPORTANT]
> **What This Dataset Can and Cannot Test:**
> 1. **No Direct Drag Factor ($k$) or Handle Drive-Length ($L$) Telemetry:** Public Time-Team race results and 1 Hz PM5 race charts record split times, average power ($P = 2.80 v^3$), stroke rate (`spm`), speed ($v$), Distance Per Stroke ($\text{DPS}$), and Work Per Stroke ($W_{\text{stroke}}$). They **do not** log the PM5 Drag Factor ($k$), physical handle travel ($L_{\text{effective}}$), or catch slip ($L_{\text{slip}}$). Therefore, this empirical analysis evaluates the **rate ($R$) vs. work-per-stroke ($W_{\text{stroke}}$) operating map across stature/weight classes** and **quarter-by-quarter pacing trajectories**, rather than directly testing drag-factor settings.
> 2. **Verified Heights Only ($n = 83$ starts across 67 athletes):** Physical stature (`verified_height_cm`) and estimated reach ($L_{\text{est}} = 0.0078 \cdot H_{\text{cm}} - 0.08\text{ m}$) are populated **strictly** for athletes matched to public [Wikidata SPARQL, Olympic/Olympedia, and NCAA/IRA collegiate varsity rosters](03-references-and-literature.md#6-empirical-regatta--anthropometric-height-data-sources) via [`data/build_athlete_heights.py`](../data/build_athlete_heights.py) using `rapidfuzz` token normalization. Unverified rowers have no fabricated height values and are analyzed solely by their recorded competition category (`sex`, `weight_class`, `age_category`).
> 3. **Pseudonymization:** Athlete names are replaced upon ingestion with a 12-character keyed SHA-256 pseudonym (`athlete_id`). Because public regatta finish times and event codes are inherently linkable to public results pages, this dataset is **pseudonymized** rather than k-anonymous.
> 4. **C.R.A.S.H.-B. & WRIC Drag Factor Rules ("The Charley Butt Rule"):** Contrary to a common misconception, C.R.A.S.H.-B. Sprints and WRIC rules **do not mandate a 130–140 drag factor**. Competitors may set the damper/drag factor to **any value they choose** prior to the start, provided it is not adjusted after the race begins ([C.R.A.S.H.-B. Official Rules & FAQ](03-references-and-literature.md#crash-b-sprints-official-drag-factor-faq--the-charley-butt-rule)). (Strict 125–140 or fixed-130 requirements come instead from national federation testing protocols such as British Rowing, Rowing Australia, and Rowing Canada; see [Section 5 of References](03-references-and-literature.md#5-championship-regatta-rules--national-federation-testing-protocols).)

| Dataset / Artifact | Records | Description |
| :--- | :--- | :--- |
| [`data/crashb_2k_summary.csv`](../data/crashb_2k_summary.csv) | **4,620** | All individual 2,000m non-adaptive race results across 8 regatta editions with 500m splits, Watts ($P = 2.80 v^3$), average stroke rate (`avg_spm`), Distance Per Stroke ($\text{DPS}$), and Work Per Stroke ($W_{\text{stroke}}$). |
| [`data/athlete_heights.csv`](../data/athlete_heights.csv) | **67** (83 races) | Reproducible lookup table of verified physical heights (`height_cm`) downloaded and matched by [`data/build_athlete_heights.py`](../data/build_athlete_heights.py), keyed by pseudonymized `athlete_id`. |
| [`data/crashb_quarter_telemetry.csv`](../data/crashb_quarter_telemetry.csv) | **400** | Quarter-by-quarter ($Q_1 \dots Q_4$) stroke rate ($R_{Q1} \dots R_{Q4}$), speed, and distance-per-stroke extracted from 1 Hz PM5 race-chart telemetry (enriched for Open/Senior, U23, Lightweight, and podium heats). |
| [`data/eval_height_vs_rate_summary.csv`](../data/eval_height_vs_rate_summary.csv) | **6** bands | Aggregated evaluation of verified height ($H$) vs. stroke rate ($R$), work per stroke, and 2k speed. |
| [`data/eval_category_summary.csv`](../data/eval_category_summary.csv) | **22** categories | Breakdown across Sex, Weight Class (`Open/Heavyweight`, `Lightweight`, `Flyweight`), and Age Category (`U15`, `U17`, `U19`, `U23`, `Open/Senior`, `Masters`). |
| [`data/eval_telemetry_pacing_summary.csv`](../data/eval_telemetry_pacing_summary.csv) | **8** cohorts | Quarter-by-quarter cadence and split pacing evaluation. |
| [`data/charts/*.svg`](../data/charts/) | **4** charts | Vector SVG charts generated via `matplotlib` by [`data/evaluate_crashb.py`](../data/evaluate_crashb.py). |

---

## 2. Finding 1: Verified Height ($H$) vs. Stroke Rate ($R$) & Work per Stroke ($n = 83$ Starts)

![Verified Height vs. Stroke Rate and Work per Stroke](../data/charts/height_vs_spm_and_work.svg)

| Sex | Stature Band | Races ($n$) | Mean Height | Est. Reach ($L$) | Mean Rate ($R$) | Mean 2k Time (Split) | Mean Power ($P$) | Work / Stroke ($W_{\text{stroke}}$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **M** | Very Tall Men (>= 198 cm / 6'6"+) | 5 | **200.6 cm** | 1.48 m | **35.3 ± 2.9 spm** | 5:54.5 (1:28.6) | 505 W | **858 J** |
| **M** | Tall Men (190 - 197 cm / 6'3" - 6'5.5") | 26 | **192.8 cm** | 1.42 m | **31.9 ± 2.9 spm** | 6:39.6 (1:39.9) | 362 W | **679 J** |
| **M** | Medium / Lwt Men (< 190 cm / <= 6'2") | 16 | **186.6 cm** | 1.38 m | **34.5 ± 4.3 spm** | 6:25.5 (1:36.4) | 402 W | **698 J** |
| **W** | Tall Women (>= 185 cm / 6'1"+) | 8 | **189.1 cm** | 1.39 m | **33.0 ± 1.3 spm** | 6:47.4 (1:41.8) | 334 W | **608 J** |
| **W** | Medium-Tall Women (178 - 184 cm / 5'10" - 6'0.5") | 10 | **179.5 cm** | 1.32 m | **31.4 ± 2.8 spm** | 7:22.5 (1:50.6) | 268 W | **509 J** |
| **W** | Shorter / Lwt Women (< 178 cm / <= 5'9") | 18 | **169.0 cm** | 1.24 m | **31.4 ± 2.7 spm** | 8:01.5 (2:00.4) | 205 W | **391 J** |

### Pooled vs. Within-Weight-Class Correlations (De-Confounding Weight Class)
Because the verified-height sample spans both `Open/Heavyweight` and `Lightweight`/`Flyweight` athletes, pooling across weight classes mixes stature with body mass. Below we report **both** the pooled regressions and the **within-weight-class** regressions:

* **Men Pooled ($n = 47$):**
  * **Height vs. Stroke Rate ($R$):** $r = -0.091$ (slope $= -0.7\text{ spm per +10 cm}$, $p = 0.5422$).
  * **Height vs. Work per Stroke ($W_{\text{stroke}}$):** $r = +0.362$ (slope $= +85\text{ J per +10 cm}$, $p = 1.24e-02$).
  * **Height vs. 2,000m Watts ($P$):** $r = +0.245$ ($p = 9.71e-02$); **Height vs. Finish Time:** $r = -0.201$ ($p = 1.76e-01$).
* **Men Within-Weight-Class:**
  * **Open/Heavyweight Men Only ($n = 41$):** Height vs. Rate $r = +0.280$ ($p = 0.076$); Height vs. Work per Stroke $r = +0.367$ ($p = 0.018$).
  * **Lightweight/Flyweight Men Only ($n = 6$):** Height vs. Rate $r = -0.949$ ($p = 0.004$).
* **Women Pooled ($n = 36$):**
  * **Height vs. Stroke Rate ($R$):** $r = +0.268$ (slope $= +0.8\text{ spm per +10 cm}$, $p = 0.1139$).
  * **Height vs. Work per Stroke ($W_{\text{stroke}}$):** $r = +0.834$ (slope $= +105\text{ J per +10 cm}$, $p = 2.60e-10$).
  * **Open/Heavyweight Women Only ($n = 30$):** Height vs. Rate $r = +0.378$ ($p = 0.039$); Height vs. Work per Stroke $r = +0.827$ ($p = 0.000$).

> **Empirical Takeaway:** In the Very Tall Men band ($\ge 198\text{ cm}$, $n = 5$), athletes average **35.3 ± 2.9 spm** and **858 J/stroke** (with 0 of 5 starts exceeding $950\text{ J/stroke}$), whereas Medium/Lightweight Men ($< 190\text{ cm}$, $n = 16$) average **34.5 spm** and **698 J/stroke**.

---

## 3. Finding 2: Weight & Age Category Comparison ($N = 4,620$ Races)

![Biomechanical Operating Map by Stature Category](../data/charts/category_operating_map.svg)

![Within-Class Stroke Rate vs. 2000m Split Pace](../data/charts/within_class_spm_vs_split.svg)

| Sex | Weight Class | Age Category | $N$ | All Mean Rate | Top-25% Rate ($R$) | Top-25% Split | Top-25% Work/Stroke | Rate vs. Time ($r$) | $p$-value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **M** | Flyweight | Open/Senior | 52 | 31.8 spm | **33.6 spm** | 1:42.9 | 574 J | `-0.466` | `0.0005` |
| **M** | Lightweight | Masters | 276 | 31.6 spm | **33.4 spm** | 1:41.2 | 610 J | `-0.369` | `0.0` |
| **M** | Lightweight | Open/Senior | 43 | 33.0 spm | **37.4 spm** | 1:35.1 | 655 J | `-0.792` | `0.0` |
| **M** | Lightweight | U19/Junior | 156 | 31.8 spm | **34.0 spm** | 1:40.7 | 608 J | `-0.475` | `0.0` |
| **M** | Lightweight | U23 | 71 | 33.3 spm | **36.5 spm** | 1:36.2 | 648 J | `-0.657` | `0.0` |
| **M** | Open/Heavyweight | Masters | 1100 | 30.7 spm | **32.1 spm** | 1:37.6 | 710 J | `-0.277` | `0.0` |
| **M** | Open/Heavyweight | Open/Senior | 158 | 32.4 spm | **35.3 spm** | 1:29.5 | 832 J | `-0.571` | `0.0` |
| **M** | Open/Heavyweight | U15/Youth | 56 | 30.6 spm | **31.2 spm** | 1:48.5 | 536 J | `-0.024` | `0.8611` |
| **M** | Open/Heavyweight | U17 | 168 | 30.6 spm | **31.2 spm** | 1:42.7 | 628 J | `-0.172` | `0.0258` |
| **M** | Open/Heavyweight | U19/Junior | 603 | 31.2 spm | **32.4 spm** | 1:37.6 | 702 J | `-0.276` | `0.0` |
| **M** | Open/Heavyweight | U23 | 121 | 31.6 spm | **33.3 spm** | 1:32.5 | 801 J | `-0.551` | `0.0` |
| **W** | Flyweight | Open/Senior | 31 | 30.9 spm | **32.8 spm** | 1:59.5 | 376 J | `-0.454` | `0.0104` |
| **W** | Lightweight | Masters | 200 | 30.7 spm | **31.8 spm** | 1:56.6 | 419 J | `-0.006` | `0.9322` |
| **W** | Lightweight | Open/Senior | 22 | 32.9 spm | **35.3 spm** | 1:50.2 | 446 J | `-0.68` | `0.0005` |
| **W** | Lightweight | U19/Junior | 80 | 30.3 spm | **32.4 spm** | 1:55.4 | 425 J | `-0.556` | `0.0` |
| **W** | Lightweight | U23 | 40 | 31.3 spm | **34.0 spm** | 1:51.0 | 454 J | `-0.584` | `0.0001` |
| **W** | Open/Heavyweight | Masters | 501 | 30.2 spm | **31.1 spm** | 1:52.6 | 477 J | `-0.076` | `0.0888` |
| **W** | Open/Heavyweight | Open/Senior | 138 | 31.0 spm | **33.4 spm** | 1:42.0 | 596 J | `-0.443` | `0.0` |
| **W** | Open/Heavyweight | U15/Youth | 28 | 30.3 spm | **29.1 spm** | 2:03.3 | 390 J | `0.258` | `0.1858` |
| **W** | Open/Heavyweight | U17 | 157 | 30.1 spm | **30.8 spm** | 1:53.8 | 466 J | `-0.252` | `0.0014` |
| **W** | Open/Heavyweight | U19/Junior | 471 | 30.2 spm | **31.1 spm** | 1:51.9 | 485 J | `-0.238` | `0.0` |
| **W** | Open/Heavyweight | U23 | 148 | 30.4 spm | **31.2 spm** | 1:50.0 | 509 J | `-0.133` | `0.1058` |

### Key Structural Observations Across the Full Dataset
1. **Elite Lightweight Men vs. Open Heavyweight Men:** In `Open/Senior` and `U23`, the top quartile of Lightweight Men averages **36.5–37.4 spm** (648–655 J/stroke), whereas `Open/Heavyweight` Men average **33.3–35.3 spm** while generating **801–832 J/stroke**.
2. **Within-Class Rate vs. Time Correlations & Age Confounding in Masters:** Across all 22 categories, `corr_spm_vs_time_r` spans **`-0.792` to `+0.258`** (and **`-0.792` to `-0.133`** across `Open/Senior` and `U23` categories). In competitive senior/collegiate cohorts (such as Open/U23 Lightweight Men at $r = -0.792$ / $-0.657$ and Open/U23 Heavyweight Men at $r = -0.571$ / $-0.551$), higher stroke rate correlates strongly with faster finish times. By contrast, in pooled `Masters` categories (which span ages 27 through 95+) and small novice `U15` heats, age and experience differences dominate finish times and attenuate the raw rate correlation.

---

## 4. Finding 3: Quarter-by-Quarter Telemetry ($Q_1 \to Q_4$, $n = 400$)

*(Note on Stratification: In the bottom two rows below, races are conditioned on their third-quarter split delta $Q_3 - Q_1$ to compare how stroke rate $R$ and Distance Per Stroke $\text{DPS}$ evolve in even-paced pieces versus positive-split fades. The $Q_3 - Q_1$ split difference is the grouping criterion itself, while the resulting rate and $\text{DPS}$ curves reflect physiological fatigue rather than a mechanical flywheel effect.)*

![PM5 Telemetry Quarter-by-Quarter Stroke Rate and Split Decay](../data/charts/telemetry_quarters_pacing.svg)

| Telemetry Cohort | Races ($n$) | $Q_1$ Rate | $Q_2$ Rate | $Q_3$ Rate | $Q_4$ Rate | $Q_1$ Split | $Q_3$ Split | $Q_3 - Q_1$ Delta | $Q_3 - Q_2$ DPS |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Men Open/Heavyweight (All Telemetry)** | 131 | 33.1 spm | 31.6 spm | 31.9 spm | **34.3 spm** | 1:36.3 | 1:38.8 | **+2.48 s** | `-0.162 m` |
| **Men Lightweight (All Telemetry)** | 70 | 34.3 spm | 32.8 spm | 33.1 spm | **35.3 spm** | 1:41.0 | 1:44.0 | **+3.05 s** | `-0.167 m` |
| **Men Flyweight (All Telemetry)** | 49 | 32.5 spm | 31.0 spm | 31.4 spm | **33.3 spm** | 1:48.5 | 1:52.3 | **+3.82 s** | `-0.206 m` |
| **Women Open/Heavyweight (All Telemetry)** | 110 | 31.9 spm | 30.8 spm | 31.2 spm | **33.4 spm** | 1:50.7 | 1:52.5 | **+1.74 s** | `-0.158 m` |
| **Women Lightweight (All Telemetry)** | 32 | 33.3 spm | 31.9 spm | 32.2 spm | **34.5 spm** | 1:54.7 | 1:58.7 | **+4.01 s** | `-0.131 m` |
| **Women Flyweight (All Telemetry)** | 8 | 33.0 spm | 31.7 spm | 32.4 spm | **35.3 spm** | 1:58.9 | 2:00.5 | **+1.62 s** | `-0.264 m` |
| **Even/Negative Split Tier (Condition: Q3-Q1 <= +1.5s)** | 194 | 33.1 spm | 32.0 spm | 32.7 spm | **35.4 spm** | 1:42.7 | 1:42.7 | **+0.05 s** | `-0.180 m` |
| **Severe Positive-Split Fade Tier (Condition: Q3-Q1 >= +4.0s)** | 95 | 32.4 spm | 30.4 spm | 30.3 spm | **31.9 spm** | 1:47.5 | 1:55.5 | **+7.98 s** | `-0.189 m` |

---

## 5. Reproducing the Pipeline & Running Verification Tests

Run the complete data, evaluation, and test pipeline from the [`data/`](../data/) directory using `make`:

```bash
cd data
make all        # Builds athlete_heights.csv, runs fetch_crashb.py, evaluate_crashb.py, and test_math.py
make test       # Runs pytest / unittest mathematical and dataset integrity verification suite
make evaluate   # Re-runs statistical evaluations and regenerates SVG charts in data/charts/
make clean-raw  # Deletes git-ignored raw HTML/telemetry caches in data/raw/
```
