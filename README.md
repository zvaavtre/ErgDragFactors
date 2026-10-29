# ErgDragFactors

**Physics, Biomechanics, and Pacing Models for Concept2 Drag Factor ($k$), Stroke Length ($L$), and Catch Slip ($L_{\text{slip}}$) in a 2,000m Ergometer Test.**

---

## Overview

In competitive indoor rowing, **nobody models the damper setting (1–10) directly** because dust inside the cage, altitude, air temperature, and barometric pressure make a "5" on one machine feel completely different from a "5" on another. Instead, physics and sports science models use the **Drag Factor ($k$)**—the flywheel's true aerodynamic deceleration rate measured by the PM5 monitor during the recovery phase ($\tau_{\text{drag}} = k\omega^2$).

This repository synthesizes the mathematical derivations (Anu Dudhia, Oxford), biomechanical models (Dr. Valery Kleshnev, BioRow), and physiological studies on optimizing **Drag Factor ($k$)**, **Effective Drive Length ($L_{\text{effective}}$)**, and **Stroke Rate ($R$)** across a 2,000m (2k) piece.

---

## Repository Contents

* **[`docs/00-tldr-height-and-style-guide.md`](docs/00-tldr-height-and-style-guide.md)** — **TL;DR Playbook:** Practical 2k stroke length, drag factor, and rate management tips broken out by rower height (Tall, Medium, Shorter) and rowing style (Diesel/Aerobic vs. Power/Strength).
* **[`docs/01-drag-factor-vs-stroke-length.md`](docs/01-drag-factor-vs-stroke-length.md)** — Core mechanical and biomechanical models relating Drag Factor ($k$), Catch Slip ($L_{\text{slip}}$), Kleshnev's Handle Drag Factor ($\text{HDF}$), and athlete anthropometry for a 2k test.
* **[`docs/02-fatigue-rate-and-catch-slip.md`](docs/02-fatigue-rate-and-catch-slip.md)** — Mathematical analysis of how varying stroke rate ($R$) under fatigue affects flywheel deceleration ($\omega_{\text{min}}$) and catch slip ($L_{\text{slip}}$), including quarter-by-quarter 2k pacing strategies.
* **[`docs/03-references-and-literature.md`](docs/03-references-and-literature.md)** — Complete annotated bibliography with links to primary physics derivations, BioRow newsletters, peer-reviewed sports science papers, and Concept2 technical guides.
* **[`AGENTS.md`](AGENTS.md)** — Attribution and agent guidelines (sourced from **Gemini 4 Argon**).

---

## Quick Reference: Optimal 2k Drag Factor & Stroke Length Lookup

| Athlete Profile | Typical 2k Drive Length ($L$) | Typical 2k Rate ($R$) | Optimal 2k Drag Factor ($k$) | Approx. Damper (Clean Cage) |
| :--- | :--- | :--- | :--- | :--- |
| **Heavyweight Men** (Tall / Long lever) | $1.40 - 1.55\text{ m}$ | $32 - 36\text{ spm}$ | **125 – 135** *(up to 140 for power-dominant)* | ~4.5 – 5.5 |
| **Lightweight Men / Heavyweight Women** | $1.25 - 1.40\text{ m}$ | $33 - 37\text{ spm}$ | **115 – 125** | ~3.5 – 4.5 |
| **Lightweight Women / Shorter Rowers** | $1.10 - 1.25\text{ m}$ | $34 - 38+\text{ spm}$ | **105 – 115** | ~3.0 – 4.0 |

---

## Key Equations at a Glance

1. **Flywheel Deceleration on Recovery:**
   $$I \frac{d\omega}{dt} = -k\omega^2 \implies \omega_{\text{min}}(R) = \frac{\omega_{\text{max}}}{1 + \frac{k}{I}\omega_{\text{max}} \left(\frac{60}{R} - T_{\text{drive}}\right)}$$
   *(where Concept2 moment of inertia $I \approx 0.1001\text{ kg}\cdot\text{m}^2$)*

2. **Effective Drive Length & Catch Slip:**
   $$L_{\text{effective}} = L_{\text{total}} - L_{\text{slip}}, \quad \text{where } L_{\text{slip}} = \frac{r^2 \cdot \omega_{\text{min}}^2}{2 \cdot a_{\text{catch}}}$$
   *(where sprocket radius $r \approx 0.014\text{ m}$ and $a_{\text{catch}}$ is initial handle acceleration)*

3. **Kleshnev’s Handle Drag Factor (HDF):**
   $$\text{HDF} = \frac{P_{\text{drive}}}{v_{\text{drive}}^3} = \frac{P_{\text{drive}}}{(L / T_{\text{drive}})^3}$$

---

## Source & Attribution

Synthesized and documented by **Gemini 4 Argon** (see [`AGENTS.md`](AGENTS.md)).

