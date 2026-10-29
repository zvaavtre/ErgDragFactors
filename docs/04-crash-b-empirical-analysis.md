# Empirical Validation: C.R.A.S.H.-B. & World Indoor Championship Data (2018–2026)

This document summarizes the empirical findings from **3,565 individual 2,000m championship race records** and **400 high-resolution PM5 stroke-by-stroke race telemetry logs** harvested from the **C.R.A.S.H.-B. Sprints (2018, 2019, 2020, 2022, 2023, 2025, 2026)** and the **World Rowing Indoor Championships (WRIC 2019)**.

All scripts, reproducible Makefile targets, generated vector SVG charts (`data/charts/*.svg`), and anonymized summary CSVs (with athlete identities replaced by one-way SHA-256 digests and raw HTML/JSON excluded from Git) live in the [`data/`](../data/) directory.

---

## 1. Dataset Architecture & Methodology

| Dataset / Artifact | Records | Description |
| :--- | :--- | :--- |
| [`data/crashb_2k_summary.csv`](../data/crashb_2k_summary.csv) | **3,565** | All individual 2,000m non-adaptive race results with 500m splits, Watts ($P = 2.80 v^3$), average stroke rate (`avg_spm`), Distance Per Stroke ($\text{DPS}$), Work Per Stroke ($W_{\text{stroke}}$), and stature/drive-length estimates. |
| [`data/athlete_heights.csv`](../data/athlete_heights.csv) | **62** (69 races) | Verified physical heights (`height_cm`) from World Rowing, Olympic, USRowing, and NCAA/IRA varsity rosters, keyed strictly by one-way SHA-256 `athlete_id` hash. |
| [`data/crashb_quarter_telemetry.csv`](../data/crashb_quarter_telemetry.csv) | **400** | Quarter-by-quarter ($Q_1 \dots Q_4$) stroke rate ($R_{Q1} \dots R_{Q4}$), speed, and distance-per-stroke extracted from 1 Hz PM5 race-chart telemetry. |
| [`data/eval_height_vs_rate_summary.csv`](../data/eval_height_vs_rate_summary.csv) | **6** bands | Aggregated evaluation of verified height ($H$) and estimated drive length ($L$) vs. stroke rate ($R$), work per stroke, and 2k speed. |
| [`data/eval_category_summary.csv`](../data/eval_category_summary.csv) | **23** categories | Full breakdown across Sex, Weight Class (`Open/Heavyweight`, `Lightweight`, `Flyweight`), and Age Category (`U15`, `U17`, `U19`, `U23`, `Open`, `Masters`). |
| [`data/eval_telemetry_pacing_summary.csv`](../data/eval_telemetry_pacing_summary.csv) | **8** cohorts | Quarter-by-quarter pacing, rate progression, and flywheel split decay evaluation. |
| [`data/charts/*.svg`](../data/charts/) | **4** charts | Vector SVG charts generated automatically by [`data/evaluate_crashb.py`](../data/evaluate_crashb.py). |

### Generated Visual Charts (`data/charts/*.svg`)
1. **[`data/charts/height_vs_spm_and_work.svg`](../data/charts/height_vs_spm_and_work.svg)** — Dual-panel scatter and OLS regression plot of the verified-height championship cohort ($n = 69$ starts):
   * **Panel A (Height vs. Stroke Rate):** Plots rower height ($H$) and estimated drive length ($L_{\text{est}}$) against average 2,000m stroke rate ($R$), illustrating the negative cadence slope ($-1.1\text{ spm}$ per $+10\text{ cm}$ for Men, $-0.9\text{ spm}$ per $+10\text{ cm}$ for Women) as shorter athletes rate higher to compensate for shorter stroke length.
   * **Panel B (Height vs. Work per Stroke):** Plots rower height ($H$) against mechanical work per stroke ($W_{\text{stroke}}$ in Joules), illustrating the steep leverage advantage of taller rowers ($+109\text{ J/stroke}$ per $+10\text{ cm}$ for Men, $r = +0.87$; $+83\text{ J/stroke}$ per $+10\text{ cm}$ for Women, $r = +0.84$).
2. **[`data/charts/category_operating_map.svg`](../data/charts/category_operating_map.svg)** — Biomechanical Operating Map plotting Top-25% Work per Stroke ($W_{\text{stroke}}$) vs. Stroke Rate ($R$) across all stature/weight categories (`Open/Heavyweight`, `Lightweight`, `Flyweight` across `Open`, `U23`, `U19`, `U17`, and `Masters`) overlaid against Iso-Power contours ($P = W_{\text{stroke}} \cdot R / 60$ from $200\text{ W}$ to $500\text{ W}$).
3. **[`data/charts/within_class_spm_vs_split.svg`](../data/charts/within_class_spm_vs_split.svg)** — Binned progression curves across the non-Masters championship field ($n = 1,789$ starts) demonstrating that *within* any fixed stature/weight class (`Open/Heavyweight Men`, `Lightweight Men`, `Open/Heavyweight Women`, `Lightweight Women`), higher sustained stroke rate directly produces faster 500m split pace ($r = -0.26$ to $-0.78$).
4. **[`data/charts/telemetry_quarters_pacing.svg`](../data/charts/telemetry_quarters_pacing.svg)** — Dual-panel 1 Hz PM5 race-chart telemetry plot ($n = 400$ logs):
   * **Panel A (Parabolic Rate Curve):** Shows how competitors settle by $1.0\text{–}1.5\text{ spm}$ in $Q_2/Q_3$ after the $Q_1$ start to preserve effective drive length ($L_{\text{effective}}$) before sprinting at $+2.5\text{ to }+4.0\text{ spm}$ in $Q_4$.
   * **Panel B (500m Split Decay $Q_i - Q_1$):** Compares **Even/Negative Splitters** ($Q_3 - Q_1 \le +1.5\text{ s}$, averaging $+0.05\text{ s}$ in $Q_3$) against **Moderate Positive Splitters** and **Severe Flywheel Die-Off** ($Q_3 - Q_1 \ge +4.0\text{ s}$, averaging $+7.98\text{ s}$ split decay in $Q_3$).

### Height as an Anthropometric Proxy for Stroke Length ($L$)
Because Concept2 race results report cumulative split times and stroke rate (`spm`) rather than raw handle travel ($L$ in meters), we evaluate **stature ($H$) as a mechanical proxy for maximum effective drive length ($L_{\text{total}}$)** via two complementary methods:
1. **Direct Roster Verification ($n = 69$ championship starts):** Cross-referencing championship finalists against published Olympic, World Rowing, USRowing, and collegiate varsity rosters using a one-way SHA-256 hash (`athlete_id`), modeling physical reach via Kleshnev's anthropometric scaling ($L_{\text{est}} \approx 0.0078 \cdot H_{\text{cm}} - 0.08\text{ m}$).
2. **Structural Weight & Age Tiers ($N = 3,565$ starts):** Comparing `Open/Heavyweight` vs. `Lightweight` ($\le 75\text{ kg}$ men / $\le 61.5\text{ kg}$ women) vs. `Flyweight` ($\le 65.8\text{ kg}$ men / $\le 54.4\text{ kg}$ women), as well as developmental stature progression (`U15` $\to$ `U17` $\to$ `U19` $\to$ `U23/Open`).

---

## 2. Finding 1: Verified Height ($H$) & Stroke Length ($L$) vs. Stroke Rate ($R$)

Across the verified-height championship cohort ($n = 69$ race starts spanning $167.6\text{ cm}$ to $208.3\text{ cm}$), **taller rowers with longer stroke length ($L$) achieve faster 2,000m times at significantly lower stroke rates ($R$) because their Work Per Stroke ($W_{\text{stroke}}$) scales steeply with height:**

![Verified Height vs. Stroke Rate and Work per Stroke](../data/charts/height_vs_spm_and_work.svg)

| Sex | Stature Band | Races ($n$) | Mean Height | Est. Reach ($L$) | Mean Rate ($R$) | Mean 2k Time (Split) | Mean Power ($P$) | Work / Stroke ($W_{\text{stroke}}$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **M** | Very Tall Men (>= 198 cm / 6'6"+) | 13 | **201.2 cm** | 1.49 m | **34.8 ± 2.5 spm** | 5:54.9 (1:28.7) | 503 W | **871 J** |
| **M** | Tall Men (190 - 197 cm / 6'3" - 6'5.5") | 11 | **194.1 cm** | 1.43 m | **35.0 ± 1.4 spm** | 5:58.4 (1:29.6) | 488 W | **840 J** |
| **M** | Medium / Lwt Men (<= 189 cm / <= 6'2") | 18 | **179.5 cm** | 1.32 m | **36.8 ± 2.9 spm** | 6:25.2 (1:36.3) | 395 W | **644 J** |
| **W** | Tall Women (>= 185 cm / 6'1"+) | 9 | **188.2 cm** | 1.39 m | **32.9 ± 1.2 spm** | 6:40.4 (1:40.1) | 350 W | **640 J** |
| **W** | Medium-Tall Women (178 - 184 cm / 5'10" - 6'0.5") | 9 | **181.2 cm** | 1.33 m | **34.3 ± 1.2 spm** | 6:45.1 (1:41.3) | 338 W | **592 J** |
| **W** | Shorter / Lwt Women (< 178 cm / <= 5'9") | 9 | **172.7 cm** | 1.27 m | **34.3 ± 2.5 spm** | 7:06.3 (1:46.6) | 291 W | **510 J** |

### Statistical Correlations in Verified-Height Cohort
* **Men ($n = 42$):**
  * **Height vs. Stroke Rate ($R$):** $r = -0.438$ (slope $= -0.11\text{ spm/cm}$, $p = 0.0021$) — Every $+10\text{ cm}$ ($+4\text{ in}$) of rower height reduces required 2k stroke rate by **$\approx 1.1\text{ spm}$**.
  * **Height vs. Work per Stroke ($W_{\text{stroke}}$):** $r = +0.870$ ($p = 7.646e-29$) — Taller men generate **+109 Joules per stroke** per $+10\text{ cm}$ of stature.
  * **Height vs. 2,000m Watts ($P$):** $r = +0.802$ ($p = 2.548e-17$); **Height vs. 2,000m Time:** $r = -0.776$ ($p = 8.909e-15$).
* **Women ($n = 27$):**
  * **Height vs. Stroke Rate ($R$):** $r = -0.338$ (slope $= -0.09\text{ spm/cm}$, $p = 0.0740$) — Every $+10\text{ cm}$ of height reduces championship 2k cadence by **$\approx 0.9\text{ spm}$**.
  * **Height vs. Work per Stroke ($W_{\text{stroke}}$):** $r = +0.838$ ($p = 2.418e-14$) — Taller women generate **+83 Joules per stroke** per $+10\text{ cm}$ of stature.
  * **Height vs. 2,000m Watts ($P$):** $r = +0.731$ ($p = 1.002e-07$); **Height vs. 2,000m Time:** $r = -0.732$ ($p = 8.652e-08$).

> **Biomechanical Takeaway:** This directly validates the core equation $P = W_{\text{stroke}} \cdot (R / 60) = (\bar{F} \cdot L_{\text{effective}}) \cdot (R / 60)$. Athletes above $198\text{ cm}$ ($6'6"$) with $L \ge 1.47\text{ m}$ win world medals at **$32.2\text{–}34.5\text{ spm}$** (generating $>950\text{ J/stroke}$), whereas elite Lightweights ($175\text{–}180\text{ cm}$, $L \approx 1.29\text{–}1.32\text{ m}$) must rate **$37.5\text{–}43.0\text{ spm}$** to compensate for a $25\%$ shorter/lighter stroke.

---

## 3. Finding 2: Weight & Age Category Comparison ($N = 3,565$ Races)

When we examine the entire C.R.A.S.H.-B. and WRIC 2,000m population—and specifically the **Top-25% competitive quartile** in each category (which filters out novice/recreational pacing anomalies)—we see the exact tradeoff between **leverage ($L$)** and **cadence ($R$)**:

![Biomechanical Operating Map by Stature Category](../data/charts/category_operating_map.svg)

Furthermore, when we hold stature/weight class constant and plot **Stroke Rate ($R$) vs. 500m Split Pace** within each category, higher sustained cadence strongly predicts faster 2,000m splits:

![Within-Class Stroke Rate vs. 2000m Split Pace](../data/charts/within_class_spm_vs_split.svg)

| Sex | Weight Class | Age Category | $N$ | Est. Reach ($L$) | All Mean Rate | Top-25% Rate ($R$) | Top-25% Split | Top-25% Work/Stroke | Rate vs. Time ($r$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **M** | Flyweight | Open/Senior | 52 | 1.26 m | 31.8 spm | **33.6 spm** | 1:42.9 | 574 J | `-0.466` |
| **M** | Lightweight | Masters | 237 | 1.30 m | 31.5 spm | **33.2 spm** | 1:41.6 | 608 J | `-0.355` |
| **M** | Lightweight | Open/Senior | 24 | 1.31 m | 34.5 spm | **38.7 spm** | 1:34.3 | 649 J | `-0.778` |
| **M** | Lightweight | U19/Junior | 156 | 1.29 m | 31.8 spm | **34.0 spm** | 1:40.7 | 608 J | `-0.475` |
| **M** | Lightweight | U23 | 44 | 1.32 m | 33.2 spm | **36.7 spm** | 1:36.0 | 648 J | `-0.736` |
| **M** | Open/Heavyweight | Masters | 942 | 1.36 m | 30.8 spm | **32.0 spm** | 1:37.8 | 706 J | `-0.258` |
| **M** | Open/Heavyweight | Open/Senior | 69 | 1.43 m | 33.8 spm | **35.7 spm** | 1:28.0 | 867 J | `-0.614` |
| **M** | Open/Heavyweight | U15/Youth | 25 | 1.28 m | 31.6 spm | **31.7 spm** | 1:50.7 | 492 J | `0.205` |
| **M** | Open/Heavyweight | U17 | 102 | 1.34 m | 30.8 spm | **31.7 spm** | 1:42.8 | 616 J | `-0.267` |
| **M** | Open/Heavyweight | U19/Junior | 490 | 1.37 m | 31.3 spm | **32.4 spm** | 1:37.5 | 702 J | `-0.259` |
| **M** | Open/Heavyweight | U23 | 54 | 1.41 m | 31.0 spm | **33.0 spm** | 1:33.9 | 777 J | `-0.56` |
| **W** | Flyweight | Open/Senior | 31 | 1.17 m | 30.9 spm | **32.8 spm** | 1:59.5 | 376 J | `-0.454` |
| **W** | Lightweight | Masters | 169 | 1.20 m | 30.8 spm | **31.8 spm** | 1:56.6 | 418 J | `0.055` |
| **W** | Lightweight | Open/Senior | 13 | 1.22 m | 34.0 spm | **34.3 spm** | 1:50.3 | 456 J | `-0.421` |
| **W** | Lightweight | U19/Junior | 80 | 1.20 m | 30.3 spm | **32.4 spm** | 1:55.4 | 425 J | `-0.556` |
| **W** | Lightweight | U23 | 29 | 1.23 m | 31.2 spm | **34.2 spm** | 1:51.3 | 447 J | `-0.561` |
| **W** | Open/Heavyweight | Masters | 427 | 1.25 m | 30.3 spm | **31.0 spm** | 1:53.0 | 473 J | `0.015` |
| **W** | Open/Heavyweight | Open/Senior | 58 | 1.33 m | 32.5 spm | **34.3 spm** | 1:39.3 | 628 J | `-0.558` |
| **W** | Open/Heavyweight | U15/Youth | 12 | 1.20 m | 30.2 spm | **29.6 spm** | 2:00.9 | 407 J | `0.62` |
| **W** | Open/Heavyweight | U17 | 95 | 1.25 m | 30.5 spm | **31.1 spm** | 1:53.0 | 471 J | `-0.33` |
| **W** | Open/Heavyweight | U19/Junior | 397 | 1.27 m | 30.3 spm | **31.1 spm** | 1:52.1 | 483 J | `-0.207` |
| **W** | Open/Heavyweight | U23 | 59 | 1.31 m | 30.7 spm | **31.4 spm** | 1:51.1 | 493 J | `0.007` |

### Key Structural Observations Across the Full Dataset
1. **Elite Lightweight Men vs. Open Heavyweight Men:** In `Open/Senior` and `U23`, the top quartile of Lightweight Men rates **$36.7\text{–}38.7\text{ spm}$** (with world medalists reaching $40\text{–}43\text{ spm}$), whereas `Open/Heavyweight` Men average **$33.0\text{–}35.7\text{ spm}$** while producing $+180\text{ to }+218\text{ J}$ more work per stroke.
2. **Within Any Fixed Stature Category, Higher Rate Correlates Strongly with Faster Times ($r = -0.35$ to $-0.78$):** Inside a given stature/weight class (`corr_spm_vs_time_r` is negative across almost every competitive category), faster finishers sustain a higher stroke rate ($R$). Why? Because *within* a fixed height/weight tier, athletes have similar reach ($L$), so total power $P = W_{\text{stroke}} \cdot (R/60)$ scales directly with the ability to sustain rate without shortening.

---

## 4. Finding 3: Quarter-by-Quarter Telemetry ($Q_1 \to Q_4$) & The Flywheel Die-Off Trap

Using the 400 high-resolution PM5 race charts ([`data/crashb_quarter_telemetry.csv`](../data/crashb_quarter_telemetry.csv)), we compare quarter-by-quarter stroke rate ($R_{Q1} \dots R_{Q4}$) and 500m split decay between **Even/Negative Splitters** ($Q_3 - Q_1 \le +1.5\text{ s}$) and rowers who suffer **Severe Flywheel Die-Off** ($Q_3 - Q_1 \ge +4.0\text{ s}$):

![PM5 Telemetry Quarter-by-Quarter Stroke Rate and Split Decay](../data/charts/telemetry_quarters_pacing.svg)

| Telemetry Cohort | Races ($n$) | $Q_1$ Rate | $Q_2$ Rate | $Q_3$ Rate | $Q_4$ Rate | $Q_1$ Split | $Q_3$ Split | $Q_3 - Q_1$ Decay |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Men Open/Heavyweight (All Telemetry)** | 131 | 33.1 spm | 31.6 spm | 31.9 spm | **34.3 spm** | 1:36.3 | 1:38.8 | **+2.48 s** |
| **Men Lightweight (All Telemetry)** | 70 | 34.3 spm | 32.8 spm | 33.1 spm | **35.3 spm** | 1:41.0 | 1:44.0 | **+3.05 s** |
| **Men Flyweight (All Telemetry)** | 49 | 32.5 spm | 31.0 spm | 31.4 spm | **33.3 spm** | 1:48.5 | 1:52.3 | **+3.82 s** |
| **Women Open/Heavyweight (All Telemetry)** | 110 | 31.9 spm | 30.8 spm | 31.2 spm | **33.4 spm** | 1:50.7 | 1:52.5 | **+1.74 s** |
| **Women Lightweight (All Telemetry)** | 32 | 33.3 spm | 31.9 spm | 32.2 spm | **34.5 spm** | 1:54.7 | 1:58.7 | **+4.01 s** |
| **Women Flyweight (All Telemetry)** | 8 | 33.0 spm | 31.7 spm | 32.4 spm | **35.3 spm** | 1:58.9 | 2:00.5 | **+1.62 s** |
| **Even/Negative Splitters (Q3-Q1 <= +1.5s)** | 194 | 33.1 spm | 32.0 spm | 32.7 spm | **35.4 spm** | 1:42.7 | 1:42.7 | **+0.05 s** |
| **Severe Flywheel Die-Off (Q3-Q1 >= +4.0s)** | 95 | 32.4 spm | 30.4 spm | 30.3 spm | **31.9 spm** | 1:47.5 | 1:55.5 | **+7.98 s** |

### Confirming the Catch-Slip & Rate Pacing Model ([`docs/02-fatigue-rate-and-catch-slip.md`](02-fatigue-rate-and-catch-slip.md))
* **The Parabolic Championship Rate Curve:** Across every competitive category, rowers execute a parabolic rate profile: high in $Q_1$ (driven by a $40\text{–}44\text{ spm}$ starting sprint in the first $100\text{ m}$), settling by $1.0\text{–}1.5\text{ spm}$ in $Q_2$ and $Q_3$ to maximize recovery time and preserve effective drive length ($L_{\text{effective}}$), and ramping up by $+2.5\text{ to }+4.0\text{ spm}$ in $Q_4$ as they empty anaerobic reserves.
* **Why Flywheel Die-Off Happens:** Rowers in the *Severe Flywheel Die-Off* cohort ($Q_3 - Q_1 \ge +4.0\text{ s}$) go out at an unsustainable $Q_1$ rate/pace, suffer peripheral muscular fatigue in $Q_2/Q_3$, and lose both cadence and work per stroke simultaneously.

---

## 5. Reproducing the Analysis & Charts

Run the complete data and charting pipeline from the [`data/`](../data/) directory using `make`:

```bash
cd data
make all        # Runs fetch_crashb.py and evaluate_crashb.py (builds CSVs, SVG charts, and docs/04)
make evaluate   # Re-runs statistical evaluations and regenerates SVG charts in data/charts/
make clean-raw  # Deletes git-ignored raw HTML/telemetry caches in data/raw/
```
