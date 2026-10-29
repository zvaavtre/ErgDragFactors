# ErgDragFactors

**Physics, Biomechanics, and Pacing Models for Concept2 Drag Factor (k), Stroke Length (L), and Catch Slip in a 2,000m Ergometer Test.**

---

## Created By - Note by Dave (zvaavtre)

I went down this rabbit hole on a whim to see how well Gemini 4 Argon worked. I've only manually tweaked a few minor bits
here and there. All of this output is from Argon as directed by me. I did have claude take a look at it came up with
some misses that argon fixed with a little prompting.

All statements should be cited back to the source publications. This is more of a summary.  The data directory has a whole 
pile of code in it that might be actually correct. I haven't personally looked at it too closely but it seems reasonable.

Dave - Oct 29, 2026





## Overview

In competitive indoor rowing, **nobody models the damper setting (1–10) directly** because dust inside the cage, altitude, air temperature, and barometric pressure make a "5" on one machine feel completely different from a "5" on another ([Concept2 Damper & Drag Factor Guide](docs/03-references-and-literature.md#concept2-damper-setting-101-and-explaining-drag-factor)). Instead, physics and sports science models use the **Drag Factor** ($k$)—the flywheel's true aerodynamic deceleration rate measured by the PM5 monitor during the recovery phase ($\tau_{\text{drag}} = k\omega^2$).

This repository synthesizes the mathematical derivations ([Anu Dudhia, Oxford](docs/03-references-and-literature.md#anu-dudhia-oxford-the-physics-of-rowing)), biomechanical models ([Dr. Valery Kleshnev, BioRow](docs/03-references-and-literature.md#valery-kleshnev-biorow-handle-drag-factor)), and physiological studies ([Kane et al., 2008 & 2013](docs/03-references-and-literature.md#kane-et-al-2008--2013-effects-of-drag-factor-and-stroke-resistance-on-rowing-physiology--economy); [Cerasola et al., 2017](docs/03-references-and-literature.md#cerasola-et-al-2017-drag-factor-on-rowing-ergometer-during-2000-m-performance); [Ingham et al., 2002](docs/03-references-and-literature.md#ingham-et-al-2002-determinants-of-2000m-rowing-ergometer-performance)) on optimizing **Drag Factor** ($k$), **Effective Drive Length** ($L_{\text{effective}}$), and **Stroke Rate** ($R$) across a 2,000m (2k) piece.

---

## Repository Contents

* **[`docs/00-tldr-height-and-style-guide.md`](docs/00-tldr-height-and-style-guide.md)** — **TL;DR Playbook:** Practical 2k stroke length, drag factor, and rate management tips broken out by rower height (Tall, Medium, Shorter) and rowing style (Diesel/Aerobic vs. Power/Strength).
* **[`docs/01-drag-factor-vs-stroke-length.md`](docs/01-drag-factor-vs-stroke-length.md)** — Core mechanical and biomechanical models relating Drag Factor ($k$), Catch Slip ($L_{\text{slip}}$), Kleshnev's Handle Drag Factor ($\text{HDF}$), and athlete anthropometry for a 2k test.
* **[`docs/02-fatigue-rate-and-catch-slip.md`](docs/02-fatigue-rate-and-catch-slip.md)** — Mathematical analysis of how varying stroke rate ($R$) under fatigue affects flywheel deceleration ($\omega_{\text{min}}$) and catch slip ($L_{\text{slip}}$), including quarter-by-quarter 2k pacing strategies.
* **[`docs/03-references-and-literature.md`](docs/03-references-and-literature.md)** — Complete annotated bibliography with links to primary physics derivations, BioRow newsletters, peer-reviewed sports science papers, and Concept2 technical guides.
* **[`docs/04-crash-b-empirical-analysis.md`](docs/04-crash-b-empirical-analysis.md)** — **Empirical Validation (2018–2026 C.R.A.S.H.-B. & WRIC Dataset):** Statistical evaluation of 4,620 individual 2,000m race records (C.R.A.S.H.-B. 2018–2020, 2022–2023, 2025–2026 & WRIC 2019) and 400 PM5 stroke-by-stroke telemetry logs comparing rower height (proxy for stroke length $L$), stroke rate ($R$), work per stroke, and split decay.
* **[`data/`](data/)** — Reproducible Python pipeline ([`build_athlete_heights.py`](data/build_athlete_heights.py), [`fetch_crashb.py`](data/fetch_crashb.py), [`evaluate_crashb.py`](data/evaluate_crashb.py), [`test_math.py`](data/test_math.py), [`Makefile`](data/Makefile)) and pseudonymized summary CSV datasets.
* **[`AGENTS.md`](AGENTS.md)** — Attribution and agent guidelines (sourced from **Gemini 4 Argon**).

---

## Quick Reference: Optimal 2k Drag Factor & Stroke Length Lookup

| [Athlete Profile](docs/00-tldr-height-and-style-guide.md#1-setup-by-rower-height) | [Typical 2k Drive Length](docs/01-drag-factor-vs-stroke-length.md#1-the-mechanical-model-catch-slip-vs-drive-length) ($L$) | [Typical 2k Rate](docs/02-fatigue-rate-and-catch-slip.md#3-the-optimal-2000m-rate-vs-slip-pacing-model) ($R$) | [Optimal 2k Drag Factor](docs/01-drag-factor-vs-stroke-length.md#4-practical-lookup-model--field-calibration-protocol) ($k$) | [Approx. Damper](docs/03-references-and-literature.md#concept2-damper-setting-101-and-explaining-drag-factor) (Clean Cage) |
| :--- | :--- | :--- | :--- | :--- |
| [**Heavyweight Men** (Tall / Long lever)](docs/00-tldr-height-and-style-guide.md#tall-rowers) | 1.40 – 1.55 m | 32 – 36 spm | **125 – 135** *([up to 140 for power-dominant](docs/00-tldr-height-and-style-guide.md#2-adjustments-by-physiology-aerobic-vs-force-dominant))* | ~4.5 – 5.5 |
| [**Lightweight Men / Heavyweight Women** (Medium height)](docs/00-tldr-height-and-style-guide.md#medium-height-rowers) | 1.25 – 1.40 m | 33 – 37 spm | **115 – 125** *([±5–8 by physiology](docs/00-tldr-height-and-style-guide.md#2-adjustments-by-physiology-aerobic-vs-force-dominant))* | ~3.5 – 4.5 |
| [**Lightweight Women / Shorter Rowers**](docs/00-tldr-height-and-style-guide.md#shorter-rowers) | 1.10 – 1.25 m | 34 – 38+ spm | **105 – 115** *([avoid high damper](docs/01-drag-factor-vs-stroke-length.md#3-the-2k-fatigue-decay-curve-stroke-length-vs-time))* | ~3.0 – 4.0 |

*For detailed setup by height and physiology, see the [**TL;DR Height & Style Playbook**](docs/00-tldr-height-and-style-guide.md). For instructions on finding your exact personal drag factor using ErgData, see the [**4 × 500m Field Calibration Protocol**](docs/01-drag-factor-vs-stroke-length.md#how-to-calibrate-your-personal-drag-factor-vs-stroke-length-sweet-spot).*

---

## Key Equations at a Glance

1. **Flywheel Deceleration on Recovery** ([Detailed Rate Model](docs/02-fatigue-rate-and-catch-slip.md#1-the-mathematical-trap-why-higher-rate--more-slip-when-tired) · [Dudhia, Oxford](docs/03-references-and-literature.md#anu-dudhia-oxford-the-physics-of-rowing)):
   $$I \frac{d\omega}{dt} = -k\omega^2 \implies \omega_{\text{min}}(R) = \frac{\omega_{\text{max}}}{1 + \frac{k}{I}\omega_{\text{max}} \left(\frac{60}{R} - T_{\text{drive}}\right)}$$
   (where Concept2 moment of inertia $I \approx 0.1001\text{ kg}\cdot\text{m}^2$)

2. **Effective Drive Length & Catch Slip** ([Detailed Catch Slip Model](docs/01-drag-factor-vs-stroke-length.md#1-the-mechanical-model-catch-slip-vs-drive-length) · [Dudhia](docs/03-references-and-literature.md#anu-dudhia-oxford-the-physics-of-rowing) · [Kleshnev, 2016](docs/03-references-and-literature.md#valery-kleshnev-the-biomechanics-of-rowing-2016--2020)):
   $$L_{\text{effective}} = L_{\text{total}} - L_{\text{slip}}, \quad \text{where } L_{\text{slip}} = \frac{r^2 \cdot \omega_{\text{min}}^2}{2 \cdot a_{\text{catch}}}$$
   (where sprocket radius $r \approx 0.014\text{ m}$ and $a_{\text{catch}}$ is initial handle acceleration)

3. **Kleshnev’s Handle Drag Factor (HDF)** ([Detailed Biomechanical Model](docs/01-drag-factor-vs-stroke-length.md#2-the-biomechanical-model-kleshnevs-handle-drag-factor-hdf) · [Kleshnev, RBN 2011/01](docs/03-references-and-literature.md#valery-kleshnev-biorow-handle-drag-factor)):
   $$\text{HDF} = \frac{P_{\text{drive}}}{v_{\text{drive}}^3} = \frac{P_{\text{drive}}}{(L / T_{\text{drive}})^3}$$

---

## Source & Attribution

Synthesized and documented by **Gemini 4 Argon** (see [`AGENTS.md`](AGENTS.md)).

