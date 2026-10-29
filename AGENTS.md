# AGENTS.md

## Attribution & Source

The research synthesis, mathematical derivations, biomechanical models, and pacing documentation in this repository were generated and compiled by **Gemini 4 Argon** (via Google Antigravity).

## Repository Context for Agents

When working in or extending `ErgDragFactors`, keep the following conventions and domain principles in mind:

1. **Core Domain Focus:**
   - **Drag Factor ($k$) vs. Damper Setting (1–10):** Always model and reference the PM5 **Drag Factor ($k$)** ($\tau_{\text{drag}} = k\omega^2$), never raw damper numbers, except as approximate clean-cage translations.
   - **Effective Drive Length ($L_{\text{effective}}$) & Catch Slip ($L_{\text{slip}}$):** Distinguish between total physical reach ($L_{\text{total}}$) and engaged flywheel travel ($L_{\text{effective}} = L_{\text{total}} - L_{\text{slip}}$).
   - **Primary Literature:** Ground any additions or calculators in the work of **Anu Dudhia** (Oxford University flywheel physics) and **Dr. Valery Kleshnev** (BioRow Handle Drag Factor $\text{HDF}$ and catch-slip telemetry).

2. **Project Structure:**
   - [`README.md`](README.md) — Overview, lookup tables, and core equations.
   - [`docs/00-tldr-height-and-style-guide.md`](docs/00-tldr-height-and-style-guide.md) — Actionable TL;DR guide broken out by rower height and physiological style.
   - [`docs/01-drag-factor-vs-stroke-length.md`](docs/01-drag-factor-vs-stroke-length.md) — Mechanical & biomechanical models for Drag Factor vs. Drive Length in a 2,000m test.
   - [`docs/02-fatigue-rate-and-catch-slip.md`](docs/02-fatigue-rate-and-catch-slip.md) — Rate ($R$) vs. Catch Slip ($L_{\text{slip}}$) optimization under fatigue across 2k quarters.
   - [`docs/03-references-and-literature.md`](docs/03-references-and-literature.md) — Primary academic, physics, and manufacturer references.
