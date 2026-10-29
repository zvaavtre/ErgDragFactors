#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib",
#   "numpy",
#   "pandas",
#   "scipy",
# ]
# ///
"""
Statistical and biomechanical evaluation of C.R.A.S.H.-B. Sprints
(2018-2020, 2022-2023, 2025-2026) and World Rowing Indoor Championships
(WRIC 2019) 2,000m data using pandas, numpy, scipy.stats, and matplotlib.

Reads pseudonymized summary CSVs in data/:
  - data/crashb_2k_summary.csv
  - data/athlete_heights.csv
  - data/crashb_quarter_telemetry.csv

Outputs:
  - data/eval_height_vs_rate_summary.csv
  - data/eval_category_summary.csv
  - data/eval_telemetry_pacing_summary.csv
  - data/charts/height_vs_spm_and_work.svg
  - data/charts/category_operating_map.svg
  - data/charts/within_class_spm_vs_split.svg
  - data/charts/telemetry_quarters_pacing.svg
  - docs/04-crash-b-empirical-analysis.md
"""

import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent
CHARTS_DIR = BASE_DIR / "charts"
DOCS_DIR = BASE_DIR.parent / "docs"

# Physical constants from Anu Dudhia (Oxford University, Physics of Rowing)
CONCEPT2_INERTIA_KGM2 = 0.1001      # Flywheel moment of inertia I (kg*m^2)
CONCEPT2_SPROCKET_RADIUS_M = 0.014  # Chain sprocket radius r (m)


def format_split(seconds: float) -> str:
    if seconds is None or pd.isna(seconds) or seconds <= 0:
        return "-"
    s_round = round(float(seconds), 1)
    mins = int(s_round // 60)
    rem = s_round - mins * 60
    return f"{mins}:{rem:04.1f}"


def ols_summary(xs, ys):
    """
    Use scipy.stats.linregress to compute exact (r, slope, intercept, t_stat, p_val).
    """
    x_arr = np.asarray(xs, dtype=float)
    y_arr = np.asarray(ys, dtype=float)
    mask = ~np.isnan(x_arr) & ~np.isnan(y_arr)
    x_arr, y_arr = x_arr[mask], y_arr[mask]
    n = len(x_arr)
    if n < 3 or np.std(x_arr) == 0 or np.std(y_arr) == 0:
        return (float("nan"), float("nan"), float("nan"), float("nan"), float("nan"))
    res = stats.linregress(x_arr, y_arr)
    r = float(res.rvalue)
    df = n - 2
    t_stat = float("inf") if abs(r) >= 1.0 else float(r * math.sqrt(df / (1.0 - r * r)))
    return (r, float(res.slope), float(res.intercept), t_stat, float(res.pvalue))


# =============================================================================
# DOMAIN PHYSICS & BIOMECHANICAL MODELS (Dudhia Oxford & Kleshnev BioRow)
# =============================================================================

def watts_from_split_500(split_500_s: float) -> float:
    """Concept2 cubic power conversion: P = 2.80 / pace^3 = 2.80 * (500 / split_500)^3."""
    v = 500.0 / split_500_s
    return 2.80 * (v ** 3)


def split_500_from_watts(watts: float) -> float:
    """Inverse Concept2 cubic power conversion: split_500 = 500 * (2.80 / P)^(1/3)."""
    return 500.0 * ((2.80 / watts) ** (1.0 / 3.0))


def work_per_stroke_from_power_rate(watts: float, spm: float) -> float:
    """Mechanical work per stroke (Joules): W_stroke = 60 * P / R."""
    return 60.0 * watts / spm


def recovery_time_s(spm: float, drive_time_s: float) -> float:
    """Recovery phase duration (seconds): T_recovery = 60 / R - T_drive."""
    return (60.0 / spm) - drive_time_s


def drag_factor_to_si(drag_factor: float) -> float:
    """Convert PM5 displayed Drag Factor (e.g., 120 -> 120e-6 N*m*s^2) to SI units."""
    return drag_factor * 1e-6 if drag_factor >= 0.01 else drag_factor


def flywheel_omega_min(
    omega_max: float,
    drag_factor: float,
    spm: float,
    drive_time_s: float,
    inertia: float = CONCEPT2_INERTIA_KGM2,
) -> float:
    """
    Anu Dudhia (Oxford) analytical solution to I * d(omega)/dt = -k * omega^2
    over the unpowered recovery phase T_recovery = 60 / R - T_drive:
      omega_min(R) = omega_max / (1 + (k / I) * omega_max * (60 / R - T_drive))
    """
    k_si = drag_factor_to_si(drag_factor)
    t_rec = recovery_time_s(spm, drive_time_s)
    return omega_max / (1.0 + (k_si / inertia) * omega_max * t_rec)


def catch_slip_m(
    omega_min: float,
    a_catch_ms2: float,
    sprocket_radius_m: float = CONCEPT2_SPROCKET_RADIUS_M,
) -> float:
    """
    Catch slip distance L_slip (meters) traveled by the handle before linear handle
    speed v_handle = a_catch * t matches sprocket speed v_engage = r * omega_min:
      L_slip = (r^2 * omega_min^2) / (2 * a_catch)
    """
    v_engage = sprocket_radius_m * omega_min
    return (v_engage ** 2) / (2.0 * a_catch_ms2)


def effective_drive_length_m(l_total_m: float, l_slip_m: float) -> float:
    """Engaged flywheel drive length: L_effective = L_total - L_slip."""
    return l_total_m - l_slip_m


def handle_drag_factor(power_drive_w: float, drive_length_m: float, drive_time_s: float) -> float:
    """
    Dr. Valery Kleshnev (BioRow RBN 2011/01) Handle Drag Factor (HDF):
      HDF = P_drive / v_drive^3 = P_drive / (L / T_drive)^3
    """
    v_drive = drive_length_m / drive_time_s
    return power_drive_w / (v_drive ** 3)


# =============================================================================
# MATPLOTLIB VECTOR SVG CHART GENERATORS
# =============================================================================

def setup_plot_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.labelweight": "bold",
        "axes.edgecolor": "#94a3b8",
        "axes.grid": True,
        "grid.color": "#e2e8f0",
        "grid.linestyle": "--",
        "grid.alpha": 0.7,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


def generate_chart_1(ver_df: pd.DataFrame, out_path: Path):
    setup_plot_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))
    fig.suptitle(
        "Verified Rower Height vs. Stroke Rate & Work per Stroke (C.R.A.S.H.-B. & WRIC Finalists)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )

    palette = {
        ("M", "Open/Heavyweight"): ("#1d4ed8", "Men Open/Hwt"),
        ("M", "Lightweight"): ("#0ea5e9", "Men Lwt"),
        ("M", "Flyweight"): ("#38bdf8", "Men Fly"),
        ("W", "Open/Heavyweight"): ("#be123c", "Women Open/Hwt"),
        ("W", "Lightweight"): ("#f43f5e", "Women Lwt"),
    }

    for (sex, wc), grp in ver_df.groupby(["sex", "weight_class"]):
        col, lbl = palette.get((sex, wc), ("#64748b", f"{sex} {wc}"))
        ax1.scatter(grp["verified_height_cm"], grp["avg_spm"], color=col, label=lbl, s=36, alpha=0.85, edgecolors="white", linewidth=0.6)
        ax2.scatter(grp["verified_height_cm"], grp["work_per_stroke_j"], color=col, label=lbl, s=36, alpha=0.85, edgecolors="white", linewidth=0.6)

    for sex, col, name in [("M", "#1d4ed8", "Men Pooled"), ("W", "#be123c", "Women Pooled")]:
        sub = ver_df[ver_df["sex"] == sex]
        if len(sub) >= 3:
            r_s, b_s, a_s, _, p_s = ols_summary(sub["verified_height_cm"], sub["avg_spm"])
            x_vals = np.linspace(sub["verified_height_cm"].min(), sub["verified_height_cm"].max(), 50)
            ax1.plot(x_vals, b_s * x_vals + a_s, color=col, linestyle="--", linewidth=1.8, label=f"{name}: r={r_s:+.2f} (p={p_s:.3f})")

            r_w, b_w, a_w, _, p_w = ols_summary(sub["verified_height_cm"], sub["work_per_stroke_j"])
            ax2.plot(x_vals, b_w * x_vals + a_w, color=col, linestyle="--", linewidth=1.8, label=f"{name}: r={r_w:+.2f} (p={p_w:.1e})")

    ax1.set_title("A. Height vs. Average 2,000m Stroke Rate (spm)")
    ax1.set_xlabel("Verified Height (cm)")
    ax1.set_ylabel("Average Stroke Rate (spm)")
    ax1.legend(fontsize=8, loc="upper right")

    ax2.set_title("B. Height vs. Mechanical Work per Stroke (J)")
    ax2.set_xlabel("Verified Height (cm)")
    ax2.set_ylabel("Work per Stroke (Joules)")
    ax2.legend(fontsize=8, loc="upper left")

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="svg")
    plt.close(fig)


def generate_chart_2(cat_df: pd.DataFrame, out_path: Path):
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 5.5))

    r_grid = np.linspace(28.5, 40.5, 100)
    for watts in (200, 250, 300, 350, 400, 450, 500):
        w_curve = watts * 60.0 / r_grid
        ax.plot(r_grid, w_curve, color="#cbd5e1", linestyle=":", linewidth=1.2)
        ax.text(40.2, watts * 60.0 / 40.2, f"{watts}W ({format_split(split_500_from_watts(watts))})", fontsize=8, color="#64748b", ha="right", va="bottom")

    color_map = {
        ("M", "Open/Heavyweight"): "#1d4ed8",
        ("M", "Lightweight"): "#0284c7",
        ("M", "Flyweight"): "#38bdf8",
        ("W", "Open/Heavyweight"): "#be123c",
        ("W", "Lightweight"): "#f43f5e",
        ("W", "Flyweight"): "#fb7185",
    }

    plot_df = cat_df[cat_df["age_category"] != "U15/Youth"].copy()
    for _, row in plot_df.iterrows():
        col = color_map.get((row["sex"], row["weight_class"]), "#64748b")
        ax.scatter(row["top25_mean_spm"], row["top25_mean_work_j"], color=col, s=70, alpha=0.9, edgecolors="white", linewidth=1.0, zorder=3)
        wc_short = "Hwt" if "Open" in row["weight_class"] else ("Lwt" if "Light" in row["weight_class"] else "Fly")
        short_age = row["age_category"].split("/")[0]
        ax.annotate(
            f"{row['sex']} {wc_short} {short_age}",
            (row["top25_mean_spm"], row["top25_mean_work_j"]),
            xytext=(5, 2),
            textcoords="offset points",
            fontsize=8.5,
            fontweight="semibold",
            color="#1e293b",
        )

    ax.set_xlim(28.5, 40.5)
    ax.set_ylim(330, 930)
    ax.set_title("Biomechanical Operating Map: Top-25% Work per Stroke vs. Stroke Rate by Category")
    ax.set_xlabel("Top-25% Category Stroke Rate R (spm)")
    ax.set_ylabel("Top-25% Work per Stroke W_stroke (Joules)")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="svg")
    plt.close(fig)


def generate_chart_3(df: pd.DataFrame, out_path: Path):
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 5.2))

    non_masters = df[df["age_category"].isin(["Open/Senior", "U23", "U19/Junior"])].copy()
    cohorts = [
        ("Men Open/Heavyweight (U19/U23/Open)", "#1d4ed8", ("M", "Open/Heavyweight")),
        ("Men Lightweight (U19/U23/Open)", "#0ea5e9", ("M", "Lightweight")),
        ("Women Open/Heavyweight (U19/U23/Open)", "#be123c", ("W", "Open/Heavyweight")),
        ("Women Lightweight (U19/U23/Open)", "#f43f5e", ("W", "Lightweight")),
    ]
    bins = [(26, 29), (29, 31), (31, 33), (33, 35), (35, 37), (37, 43)]

    for label, col, (sex, wc) in cohorts:
        sub = non_masters[(non_masters["sex"] == sex) & (non_masters["weight_class"] == wc)]
        r_val, slope, _, _, _ = ols_summary(sub["avg_spm"], sub["avg_split_500_s"])
        xs, ys = [], []
        for b0, b1 in bins:
            b_sub = sub[(sub["avg_spm"] >= b0) & (sub["avg_spm"] < b1)]
            if len(b_sub) >= 4:
                xs.append(b_sub["avg_spm"].mean())
                ys.append(b_sub["avg_split_500_s"].mean())
        if len(xs) >= 2:
            ax.plot(xs, ys, marker="o", color=col, linewidth=2.2, label=f"{label} (n={len(sub)}, r={r_val:+.2f}, {slope:+.2f}s/spm)")

    ax.invert_yaxis()
    yticks = list(range(85, 126, 5))
    ax.set_yticks(yticks)
    ax.set_yticklabels([format_split(y) for y in yticks])
    ax.set_title("Within-Class Stroke Rate vs. 500m Split Pace (Non-Masters Championship Field)")
    ax.set_xlabel("Average 2,000m Stroke Rate (spm)")
    ax.set_ylabel("500m Split Pace (Faster ↑)")
    ax.legend(fontsize=8.5, loc="lower left")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="svg")
    plt.close(fig)


def generate_chart_4(tel_df: pd.DataFrame, out_path: Path):
    setup_plot_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.0))
    fig.suptitle(
        f"PM5 Race-Chart Telemetry (n = {len(tel_df)}): Quarter-by-Quarter Cadence & Pacing Stratification",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )

    q_x = [1, 2, 3, 4]
    q_labels = ["Q1 (0–500m)", "Q2 (500–1000m)", "Q3 (1000–1500m)", "Q4 (1500–2000m)"]

    cohorts = [
        ("Men Lightweight", "#0284c7", tel_df[(tel_df["sex"] == "M") & (tel_df["weight_class"] == "Lightweight")]),
        ("Women Lightweight", "#f43f5e", tel_df[(tel_df["sex"] == "W") & (tel_df["weight_class"] == "Lightweight")]),
        ("Men Open/Hwt", "#1d4ed8", tel_df[(tel_df["sex"] == "M") & (tel_df["weight_class"] == "Open/Heavyweight")]),
        ("Women Open/Hwt", "#be123c", tel_df[(tel_df["sex"] == "W") & (tel_df["weight_class"] == "Open/Heavyweight")]),
    ]
    for lbl, col, grp in cohorts:
        if len(grp) > 0:
            means = [grp[f"q{q}_spm"].mean() for q in q_x]
            ax1.plot(q_x, means, marker="o", color=col, linewidth=2.0, label=f"{lbl} (n={len(grp)})")

    ax1.set_xticks(q_x)
    ax1.set_xticklabels(q_labels, fontsize=8.5)
    ax1.set_title("A. Parabolic Championship Cadence Curve (Q1 → Q4)")
    ax1.set_ylabel("Quarter Stroke Rate (spm)")
    ax1.legend(fontsize=8.5)

    valid_splits = tel_df.dropna(subset=["split_q1_s", "split_q2_s", "split_q3_s", "split_q4_s"]).copy()
    valid_splits["q3_q1_delta"] = valid_splits["split_q3_s"] - valid_splits["split_q1_s"]

    tiers = [
        ("Even / Negative Split (Q3−Q1 ≤ +1.5s)", "#059669", valid_splits[valid_splits["q3_q1_delta"] <= 1.5]),
        ("Moderate Positive Split (+1.5s < Q3−Q1 < +4.0s)", "#d97706", valid_splits[(valid_splits["q3_q1_delta"] > 1.5) & (valid_splits["q3_q1_delta"] < 4.0)]),
        ("Severe Positive-Split Fade (Q3−Q1 ≥ +4.0s)", "#dc2626", valid_splits[valid_splits["q3_q1_delta"] >= 4.0]),
    ]
    ax2.axhline(0.0, color="#0f172a", linestyle="--", linewidth=1.0)
    for lbl, col, grp in tiers:
        if len(grp) > 0:
            deltas = [
                0.0,
                (grp["split_q2_s"] - grp["split_q1_s"]).mean(),
                (grp["split_q3_s"] - grp["split_q1_s"]).mean(),
                (grp["split_q4_s"] - grp["split_q1_s"]).mean(),
            ]
            ax2.plot(q_x, deltas, marker="o", color=col, linewidth=2.2, label=f"{lbl} (n={len(grp)})")

    ax2.set_xticks(q_x)
    ax2.set_xticklabels(q_labels, fontsize=8.5)
    ax2.set_title("B. Split Delta vs. Q1 by Pacing Tier (Conditioned on Q3−Q1)")
    ax2.set_ylabel("Split Delta vs. Q1 (s/500m, Lower = Faster)")
    ax2.legend(fontsize=8)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="svg")
    plt.close(fig)


def verify_math() -> None:
    """
    Verify statistical and biomechanical functions against scipy.stats and
    analytical invariants.
    """
    # 1. Verify ols_summary matches scipy.stats.pearsonr and linregress
    xs = np.array([170.0, 175.0, 180.0, 185.0, 190.0, 195.0, 200.0, 205.0])
    ys = np.array([38.2, 36.9, 36.1, 35.0, 34.8, 33.5, 33.1, 32.0])
    r, slope, intercept, _, p_val = ols_summary(xs, ys)
    pr = stats.pearsonr(xs, ys)
    assert math.isclose(r, pr.statistic, rel_tol=1e-13)
    assert math.isclose(p_val, pr.pvalue, rel_tol=1e-13)
    assert math.isclose(slope * np.mean(xs) + intercept, np.mean(ys), rel_tol=1e-13)

    # 2. Verify Dudhia flywheel ODE invariant: 1/omega_min - 1/omega_max == (k/I)*T_rec
    omega_max = 145.0
    df_pm5 = 125.0
    spm = 34.0
    t_drive = 0.72
    t_rec = recovery_time_s(spm, t_drive)
    w_min = flywheel_omega_min(omega_max, df_pm5, spm, t_drive)
    k_si = drag_factor_to_si(df_pm5)
    assert math.isclose(
        (1.0 / w_min) - (1.0 / omega_max),
        (k_si / CONCEPT2_INERTIA_KGM2) * t_rec,
        rel_tol=1e-14,
    )

    # 3. Verify Catch Slip & Kleshnev HDF
    slip = catch_slip_m(w_min, 12.5)
    assert math.isclose(effective_drive_length_m(1.42, slip) + slip, 1.42, rel_tol=1e-14)
    assert math.isclose(handle_drag_factor(600.0, 1.40, 0.70), 75.0, rel_tol=1e-14)
    assert math.isclose(watts_from_split_500(100.0), 350.0, rel_tol=1e-13)
    assert math.isclose(split_500_from_watts(350.0), 100.0, rel_tol=1e-13)


def main():
    verify_math()
    if "--test" in sys.argv:
        print("evaluate_crashb.py: all mathematical assertions passed.")
        return

    df = pd.read_csv(BASE_DIR / "crashb_2k_summary.csv")
    tel_path = BASE_DIR / "crashb_quarter_telemetry.csv"
    tel_df = pd.read_csv(tel_path) if tel_path.exists() else pd.DataFrame()

    # =========================================================================
    # 1. VERIFIED HEIGHT COHORT EVALUATION (De-confounded by Weight Class)
    # =========================================================================
    ver_df = df.dropna(subset=["verified_height_cm"]).copy()
    ver_m = ver_df[ver_df["sex"] == "M"]
    ver_w = ver_df[ver_df["sex"] == "W"]
    ver_m_hwt = ver_m[ver_m["weight_class"] == "Open/Heavyweight"]
    ver_m_lwt = ver_m[ver_m["weight_class"].isin(["Lightweight", "Flyweight"])]
    ver_w_hwt = ver_w[ver_w["weight_class"] == "Open/Heavyweight"]

    corr_m_h_spm = ols_summary(ver_m["verified_height_cm"], ver_m["avg_spm"])
    corr_m_h_work = ols_summary(ver_m["verified_height_cm"], ver_m["work_per_stroke_j"])
    corr_m_h_watts = ols_summary(ver_m["verified_height_cm"], ver_m["avg_watts"])
    corr_m_h_time = ols_summary(ver_m["verified_height_cm"], ver_m["finish_time_s"])

    corr_m_hwt_spm = ols_summary(ver_m_hwt["verified_height_cm"], ver_m_hwt["avg_spm"])
    corr_m_hwt_work = ols_summary(ver_m_hwt["verified_height_cm"], ver_m_hwt["work_per_stroke_j"])
    corr_m_lwt_spm = ols_summary(ver_m_lwt["verified_height_cm"], ver_m_lwt["avg_spm"])

    corr_w_h_spm = ols_summary(ver_w["verified_height_cm"], ver_w["avg_spm"])
    corr_w_h_work = ols_summary(ver_w["verified_height_cm"], ver_w["work_per_stroke_j"])
    corr_w_h_watts = ols_summary(ver_w["verified_height_cm"], ver_w["avg_watts"])
    corr_w_h_time = ols_summary(ver_w["verified_height_cm"], ver_w["finish_time_s"])
    corr_w_hwt_spm = ols_summary(ver_w_hwt["verified_height_cm"], ver_w_hwt["avg_spm"])
    corr_w_hwt_work = ols_summary(ver_w_hwt["verified_height_cm"], ver_w_hwt["work_per_stroke_j"])

    height_bands = [
        ("M", "Very Tall Men (>= 198 cm / 6'6\"+)", ver_m[ver_m["verified_height_cm"] >= 198.0]),
        ("M", "Tall Men (190 - 197 cm / 6'3\" - 6'5.5\")", ver_m[(ver_m["verified_height_cm"] >= 190.0) & (ver_m["verified_height_cm"] < 198.0)]),
        ("M", "Medium / Lwt Men (< 190 cm / <= 6'2\")", ver_m[ver_m["verified_height_cm"] < 190.0]),
        ("W", "Tall Women (>= 185 cm / 6'1\"+)", ver_w[ver_w["verified_height_cm"] >= 185.0]),
        ("W", "Medium-Tall Women (178 - 184 cm / 5'10\" - 6'0.5\")", ver_w[(ver_w["verified_height_cm"] >= 178.0) & (ver_w["verified_height_cm"] < 185.0)]),
        ("W", "Shorter / Lwt Women (< 178 cm / <= 5'9\")", ver_w[ver_w["verified_height_cm"] < 178.0]),
    ]

    height_summary_rows = []
    for sex, label, sub in height_bands:
        if len(sub) == 0:
            continue
        height_summary_rows.append({
            "sex": sex,
            "stature_band": label,
            "n_races": len(sub),
            "mean_height_cm": round(float(sub["verified_height_cm"].mean()), 1),
            "mean_est_drive_length_m": round(float(sub["est_drive_length_m"].mean()), 3),
            "mean_spm": round(float(sub["avg_spm"].mean()), 2),
            "sd_spm": round(float(sub["avg_spm"].std(ddof=1)), 2) if len(sub) > 1 else 0.0,
            "mean_finish_time_s": round(float(sub["finish_time_s"].mean()), 1),
            "mean_split_500": format_split(sub["avg_split_500_s"].mean()),
            "mean_watts": round(float(sub["avg_watts"].mean()), 1),
            "mean_work_per_stroke_j": round(float(sub["work_per_stroke_j"].mean()), 1),
            "mean_dps_m": round(float(sub["dps_m"].mean()), 2),
        })

    out_height_csv = BASE_DIR / "eval_height_vs_rate_summary.csv"
    pd.DataFrame(height_summary_rows).to_csv(out_height_csv, index=False)

    # =========================================================================
    # 2. FULL DATASET CATEGORY EVALUATION
    # =========================================================================
    cat_summary_rows = []
    for (sex, wc, age_cat), grp in df.groupby(["sex", "weight_class", "age_category"]):
        if len(grp) < 3:
            continue
        grp_sorted = grp.sort_values("finish_time_s")
        top25 = grp_sorted.iloc[: max(3, len(grp_sorted) // 4)]
        r_val, _, _, _, p_val = ols_summary(grp["avg_spm"], grp["finish_time_s"])
        cat_summary_rows.append({
            "sex": sex,
            "weight_class": wc,
            "age_category": age_cat,
            "n_total": len(grp),
            "mean_spm_all": round(float(grp["avg_spm"].mean()), 2),
            "sd_spm_all": round(float(grp["avg_spm"].std(ddof=1)), 2),
            "mean_time_s_all": round(float(grp["finish_time_s"].mean()), 1),
            "mean_split_all": format_split(grp["avg_split_500_s"].mean()),
            "mean_watts_all": round(float(grp["avg_watts"].mean()), 1),
            "mean_work_j_all": round(float(grp["work_per_stroke_j"].mean()), 1),
            "top25_mean_spm": round(float(top25["avg_spm"].mean()), 2),
            "top25_mean_time_s": round(float(top25["finish_time_s"].mean()), 1),
            "top25_mean_split": format_split(top25["avg_split_500_s"].mean()),
            "top25_mean_watts": round(float(top25["avg_watts"].mean()), 1),
            "top25_mean_work_j": round(float(top25["work_per_stroke_j"].mean()), 1),
            "corr_spm_vs_time_r": round(r_val, 3) if not math.isnan(r_val) else "",
            "corr_spm_vs_time_p": round(p_val, 4) if not math.isnan(p_val) else "",
        })

    cat_df = pd.DataFrame(cat_summary_rows)
    out_cat_csv = BASE_DIR / "eval_category_summary.csv"
    cat_df.to_csv(out_cat_csv, index=False)

    # =========================================================================
    # 3. QUARTER-BY-QUARTER PM5 TELEMETRY EVALUATION
    # =========================================================================
    pacing_summary_rows = []
    if len(tel_df) > 0:
        valid_q = tel_df.dropna(subset=["split_q1_s", "split_q3_s"]).copy()
        valid_q["q3_q1_delta"] = valid_q["split_q3_s"] - valid_q["split_q1_s"]

        t_groups = [
            ("Men Open/Heavyweight (All Telemetry)", tel_df[(tel_df["sex"] == "M") & (tel_df["weight_class"] == "Open/Heavyweight")]),
            ("Men Lightweight (All Telemetry)", tel_df[(tel_df["sex"] == "M") & (tel_df["weight_class"] == "Lightweight")]),
            ("Men Flyweight (All Telemetry)", tel_df[(tel_df["sex"] == "M") & (tel_df["weight_class"] == "Flyweight")]),
            ("Women Open/Heavyweight (All Telemetry)", tel_df[(tel_df["sex"] == "W") & (tel_df["weight_class"] == "Open/Heavyweight")]),
            ("Women Lightweight (All Telemetry)", tel_df[(tel_df["sex"] == "W") & (tel_df["weight_class"] == "Lightweight")]),
            ("Women Flyweight (All Telemetry)", tel_df[(tel_df["sex"] == "W") & (tel_df["weight_class"] == "Flyweight")]),
            ("Even/Negative Split Tier (Condition: Q3-Q1 <= +1.5s)", valid_q[valid_q["q3_q1_delta"] <= 1.5]),
            ("Severe Positive-Split Fade Tier (Condition: Q3-Q1 >= +4.0s)", valid_q[valid_q["q3_q1_delta"] >= 4.0]),
        ]

        for label, grp in t_groups:
            if len(grp) == 0:
                continue
            q1_s = grp["split_q1_s"].dropna()
            q2_s = grp["split_q2_s"].dropna()
            q3_s = grp["split_q3_s"].dropna()
            q4_s = grp["split_q4_s"].dropna()
            pacing_summary_rows.append({
                "cohort": label,
                "n_races": len(grp),
                "q1_spm": round(float(grp["q1_spm"].mean()), 2),
                "q2_spm": round(float(grp["q2_spm"].mean()), 2),
                "q3_spm": round(float(grp["q3_spm"].mean()), 2),
                "q4_spm": round(float(grp["q4_spm"].mean()), 2),
                "q1_dps_m": round(float(grp["q1_dps_m"].mean()), 2),
                "q2_dps_m": round(float(grp["q2_dps_m"].mean()), 2),
                "q3_dps_m": round(float(grp["q3_dps_m"].mean()), 2),
                "q4_dps_m": round(float(grp["q4_dps_m"].mean()), 2),
                "q1_split_s": round(float(q1_s.mean()), 2) if len(q1_s) else "",
                "q2_split_s": round(float(q2_s.mean()), 2) if len(q2_s) else "",
                "q3_split_s": round(float(q3_s.mean()), 2) if len(q3_s) else "",
                "q4_split_s": round(float(q4_s.mean()), 2) if len(q4_s) else "",
                "q3_minus_q1_split_s": round(float(q3_s.mean() - q1_s.mean()), 2) if (len(q1_s) and len(q3_s)) else "",
                "q3_minus_q2_dps_m": round(float((grp["q3_dps_m"] - grp["q2_dps_m"]).mean()), 3),
            })

        out_pacing_csv = BASE_DIR / "eval_telemetry_pacing_summary.csv"
        pd.DataFrame(pacing_summary_rows).to_csv(out_pacing_csv, index=False)

    # =========================================================================
    # 4. GENERATE VECTOR SVG CHARTS VIA MATPLOTLIB
    # =========================================================================
    generate_chart_1(ver_df, CHARTS_DIR / "height_vs_spm_and_work.svg")
    generate_chart_2(cat_df, CHARTS_DIR / "category_operating_map.svg")
    generate_chart_3(df, CHARTS_DIR / "within_class_spm_vs_split.svg")
    if len(tel_df) > 0:
        generate_chart_4(tel_df, CHARTS_DIR / "telemetry_quarters_pacing.svg")

    # =========================================================================
    # 5. GENERATE MARKDOWN REPORT WITH DYNAMICALLY COMPUTED METRICS
    # =========================================================================
    vt_men = ver_m[ver_m["verified_height_cm"] >= 198.0]
    n_vt_above_950 = int((vt_men["work_per_stroke_j"] > 950.0).sum())
    n_unique_heights = int(ver_df["athlete_id"].nunique())

    open_u23_cats = cat_df[cat_df["age_category"].isin(["Open/Senior", "U23"])].copy()
    open_u23_rs = [float(x) for x in open_u23_cats["corr_spm_vs_time_r"] if x != ""]
    all_rs = [float(x) for x in cat_df["corr_spm_vs_time_r"] if x != ""]

    lwt_open_m = cat_df[(cat_df["sex"] == "M") & (cat_df["weight_class"] == "Lightweight") & (cat_df["age_category"] == "Open/Senior")].iloc[0]
    lwt_u23_m = cat_df[(cat_df["sex"] == "M") & (cat_df["weight_class"] == "Lightweight") & (cat_df["age_category"] == "U23")].iloc[0]
    hwt_open_m = cat_df[(cat_df["sex"] == "M") & (cat_df["weight_class"] == "Open/Heavyweight") & (cat_df["age_category"] == "Open/Senior")].iloc[0]
    hwt_u23_m = cat_df[(cat_df["sex"] == "M") & (cat_df["weight_class"] == "Open/Heavyweight") & (cat_df["age_category"] == "U23")].iloc[0]

    report_path = DOCS_DIR / "04-crash-b-empirical-analysis.md"
    lines = [
        "# Empirical Analysis: C.R.A.S.H.-B. & World Indoor Championship Data (2018–2026)",
        "",
        f"This document summarizes the empirical findings from **{len(df):,} individual 2,000m championship race records** and **{len(tel_df):,} 1 Hz PM5 race-chart telemetry logs** harvested from the **C.R.A.S.H.-B. Sprints (2018, 2019, 2020, 2022, 2023, 2025, 2026)** and the **World Rowing Indoor Championships (WRIC 2019)**.",
        "",
        "*(Note: The 2021 and 2024 C.R.A.S.H.-B. editions are not hosted on the Time-Team regatta server and are not included in this dataset.)*",
        "",
        "---",
        "",
        "## 1. Scope, Methodological Limitations & Dataset Architecture",
        "",
        "> [!IMPORTANT]",
        "> **What This Dataset Can and Cannot Test:**",
        "> 1. **No Direct Drag Factor ($k$) or Handle Drive-Length ($L$) Telemetry:** Public Time-Team race results and 1 Hz PM5 race charts record split times, average power ($P = 2.80 v^3$), stroke rate (`spm`), speed ($v$), Distance Per Stroke ($\\text{DPS}$), and Work Per Stroke ($W_{\\text{stroke}}$). They **do not** log the PM5 Drag Factor ($k$), physical handle travel ($L_{\\text{effective}}$), or catch slip ($L_{\\text{slip}}$). Therefore, this empirical analysis evaluates the **rate ($R$) vs. work-per-stroke ($W_{\\text{stroke}}$) operating map across stature/weight classes** and **quarter-by-quarter pacing trajectories**, rather than directly testing drag-factor settings.",
        f"> 2. **Verified Heights Only ($n = {len(ver_df)}$ starts across {n_unique_heights} athletes):** Physical stature (`verified_height_cm`) and estimated reach ($L_{{\\text{{est}}}} = 0.0078 \\cdot H_{{\\text{{cm}}}} - 0.08\\text{{ m}}$) are populated **strictly** for athletes matched to public [Wikidata SPARQL, Olympic/Olympedia, and NCAA/IRA collegiate varsity rosters](03-references-and-literature.md#6-empirical-regatta--anthropometric-height-data-sources) via [`data/build_athlete_heights.py`](../data/build_athlete_heights.py) using `rapidfuzz` token normalization. Unverified rowers have no fabricated height values and are analyzed solely by their recorded competition category (`sex`, `weight_class`, `age_category`).",
        "> 3. **Pseudonymization:** Athlete names are replaced upon ingestion with a 12-character keyed SHA-256 pseudonym (`athlete_id`). Because public regatta finish times and event codes are inherently linkable to public results pages, this dataset is **pseudonymized** rather than k-anonymous.",
        "> 4. **C.R.A.S.H.-B. & WRIC Drag Factor Rules (\"The Charley Butt Rule\"):** Contrary to a common misconception, C.R.A.S.H.-B. Sprints and WRIC rules **do not mandate a 130–140 drag factor**. Competitors may set the damper/drag factor to **any value they choose** prior to the start, provided it is not adjusted after the race begins ([C.R.A.S.H.-B. Official Rules & FAQ](03-references-and-literature.md#crash-b-sprints-official-drag-factor-faq--the-charley-butt-rule)). (Strict 125–140 or fixed-130 requirements come instead from national federation testing protocols such as British Rowing, Rowing Australia, and Rowing Canada; see [Section 5 of References](03-references-and-literature.md#5-championship-regatta-rules--national-federation-testing-protocols).)",
        "",
        "| Dataset / Artifact | Records | Description |",
        "| :--- | :--- | :--- |",
        f"| [`data/crashb_2k_summary.csv`](../data/crashb_2k_summary.csv) | **{len(df):,}** | All individual 2,000m non-adaptive race results across 8 regatta editions with 500m splits, Watts ($P = 2.80 v^3$), average stroke rate (`avg_spm`), Distance Per Stroke ($\\text{{DPS}}$), and Work Per Stroke ($W_{{\\text{{stroke}}}}$). |",
        f"| [`data/athlete_heights.csv`](../data/athlete_heights.csv) | **{n_unique_heights}** ({len(ver_df)} races) | Reproducible lookup table of verified physical heights (`height_cm`) downloaded and matched by [`data/build_athlete_heights.py`](../data/build_athlete_heights.py), keyed by pseudonymized `athlete_id`. |",
        f"| [`data/crashb_quarter_telemetry.csv`](../data/crashb_quarter_telemetry.csv) | **{len(tel_df):,}** | Quarter-by-quarter ($Q_1 \\dots Q_4$) stroke rate ($R_{{Q1}} \\dots R_{{Q4}}$), speed, and distance-per-stroke extracted from 1 Hz PM5 race-chart telemetry (enriched for Open/Senior, U23, Lightweight, and podium heats). |",
        f"| [`data/eval_height_vs_rate_summary.csv`](../data/eval_height_vs_rate_summary.csv) | **{len(height_summary_rows)}** bands | Aggregated evaluation of verified height ($H$) vs. stroke rate ($R$), work per stroke, and 2k speed. |",
        f"| [`data/eval_category_summary.csv`](../data/eval_category_summary.csv) | **{len(cat_df)}** categories | Breakdown across Sex, Weight Class (`Open/Heavyweight`, `Lightweight`, `Flyweight`), and Age Category (`U15`, `U17`, `U19`, `U23`, `Open/Senior`, `Masters`). |",
        f"| [`data/eval_telemetry_pacing_summary.csv`](../data/eval_telemetry_pacing_summary.csv) | **{len(pacing_summary_rows)}** cohorts | Quarter-by-quarter cadence and split pacing evaluation. |",
        "| [`data/charts/*.svg`](../data/charts/) | **4** charts | Vector SVG charts generated via `matplotlib` by [`data/evaluate_crashb.py`](../data/evaluate_crashb.py). |",
        "",
        "---",
        "",
        f"## 2. Finding 1: Verified Height ($H$) vs. Stroke Rate ($R$) & Work per Stroke ($n = {len(ver_df)}$ Starts)",
        "",
        "![Verified Height vs. Stroke Rate and Work per Stroke](../data/charts/height_vs_spm_and_work.svg)",
        "",
        "| Sex | Stature Band | Races ($n$) | Mean Height | Est. Reach ($L$) | Mean Rate ($R$) | Mean 2k Time (Split) | Mean Power ($P$) | Work / Stroke ($W_{\\text{stroke}}$) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for hr in height_summary_rows:
        t_fmt = format_split(hr["mean_finish_time_s"])
        lines.append(
            f"| **{hr['sex']}** | {hr['stature_band']} | {hr['n_races']} | "
            f"**{hr['mean_height_cm']:.1f} cm** | {hr['mean_est_drive_length_m']:.2f} m | "
            f"**{hr['mean_spm']:.1f} ± {hr['sd_spm']:.1f} spm** | {t_fmt} ({hr['mean_split_500']}) | "
            f"{hr['mean_watts']:.0f} W | **{hr['mean_work_per_stroke_j']:.0f} J** |"
        )

    lines.extend([
        "",
        "### Pooled vs. Within-Weight-Class Correlations (De-Confounding Weight Class)",
        "Because the verified-height sample spans both `Open/Heavyweight` and `Lightweight`/`Flyweight` athletes, pooling across weight classes mixes stature with body mass. Below we report **both** the pooled regressions and the **within-weight-class** regressions:",
        "",
        f"* **Men Pooled ($n = {len(ver_m)}$):**",
        f"  * **Height vs. Stroke Rate ($R$):** $r = {corr_m_h_spm[0]:+.3f}$ (slope $= {corr_m_h_spm[1]*10:+.1f}\\text{{ spm per +10 cm}}$, $p = {corr_m_h_spm[4]:.4f}$).",
        f"  * **Height vs. Work per Stroke ($W_{{\\text{{stroke}}}}$):** $r = {corr_m_h_work[0]:+.3f}$ (slope $= {corr_m_h_work[1]*10:+.0f}\\text{{ J per +10 cm}}$, $p = {corr_m_h_work[4]:.2e}$).",
        f"  * **Height vs. 2,000m Watts ($P$):** $r = {corr_m_h_watts[0]:+.3f}$ ($p = {corr_m_h_watts[4]:.2e}$); **Height vs. Finish Time:** $r = {corr_m_h_time[0]:+.3f}$ ($p = {corr_m_h_time[4]:.2e}$).",
        f"* **Men Within-Weight-Class:**",
        f"  * **Open/Heavyweight Men Only ($n = {len(ver_m_hwt)}$):** Height vs. Rate $r = {corr_m_hwt_spm[0]:+.3f}$ ($p = {corr_m_hwt_spm[4]:.3f}$); Height vs. Work per Stroke $r = {corr_m_hwt_work[0]:+.3f}$ ($p = {corr_m_hwt_work[4]:.3f}$).",
        f"  * **Lightweight/Flyweight Men Only ($n = {len(ver_m_lwt)}$):** Height vs. Rate $r = {corr_m_lwt_spm[0]:+.3f}$ ($p = {corr_m_lwt_spm[4]:.3f}$).",
        f"* **Women Pooled ($n = {len(ver_w)}$):**",
        f"  * **Height vs. Stroke Rate ($R$):** $r = {corr_w_h_spm[0]:+.3f}$ (slope $= {corr_w_h_spm[1]*10:+.1f}\\text{{ spm per +10 cm}}$, $p = {corr_w_h_spm[4]:.4f}$).",
        f"  * **Height vs. Work per Stroke ($W_{{\\text{{stroke}}}}$):** $r = {corr_w_h_work[0]:+.3f}$ (slope $= {corr_w_h_work[1]*10:+.0f}\\text{{ J per +10 cm}}$, $p = {corr_w_h_work[4]:.2e}$).",
        f"  * **Open/Heavyweight Women Only ($n = {len(ver_w_hwt)}$):** Height vs. Rate $r = {corr_w_hwt_spm[0]:+.3f}$ ($p = {corr_w_hwt_spm[4]:.3f}$); Height vs. Work per Stroke $r = {corr_w_hwt_work[0]:+.3f}$ ($p = {corr_w_hwt_work[4]:.3f}$).",
        "",
        f"> **Empirical Takeaway:** In the Very Tall Men band ($\\ge 198\\text{{ cm}}$, $n = {len(vt_men)}$), athletes average **{vt_men['avg_spm'].mean():.1f} ± {vt_men['avg_spm'].std(ddof=1):.1f} spm** and **{vt_men['work_per_stroke_j'].mean():.0f} J/stroke** (with {n_vt_above_950} of {len(vt_men)} starts exceeding $950\\text{{ J/stroke}}$), whereas Medium/Lightweight Men ($< 190\\text{{ cm}}$, $n = {len(ver_m[ver_m['verified_height_cm'] < 190.0])}$) average **{ver_m[ver_m['verified_height_cm'] < 190.0]['avg_spm'].mean():.1f} spm** and **{ver_m[ver_m['verified_height_cm'] < 190.0]['work_per_stroke_j'].mean():.0f} J/stroke**.",
        "",
        "---",
        "",
        f"## 3. Finding 2: Weight & Age Category Comparison ($N = {len(df):,}$ Races)",
        "",
        "![Biomechanical Operating Map by Stature Category](../data/charts/category_operating_map.svg)",
        "",
        "![Within-Class Stroke Rate vs. 2000m Split Pace](../data/charts/within_class_spm_vs_split.svg)",
        "",
        "| Sex | Weight Class | Age Category | $N$ | All Mean Rate | Top-25% Rate ($R$) | Top-25% Split | Top-25% Work/Stroke | Rate vs. Time ($r$) | $p$-value |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    for _, cr in cat_df.iterrows():
        lines.append(
            f"| **{cr['sex']}** | {cr['weight_class']} | {cr['age_category']} | {cr['n_total']} | "
            f"{cr['mean_spm_all']:.1f} spm | **{cr['top25_mean_spm']:.1f} spm** | {cr['top25_mean_split']} | "
            f"{cr['top25_mean_work_j']:.0f} J | `{cr['corr_spm_vs_time_r']}` | `{cr['corr_spm_vs_time_p']}` |"
        )

    lines.extend([
        "",
        "### Key Structural Observations Across the Full Dataset",
        f"1. **Elite Lightweight Men vs. Open Heavyweight Men:** In `Open/Senior` and `U23`, the top quartile of Lightweight Men averages **{lwt_u23_m['top25_mean_spm']:.1f}–{lwt_open_m['top25_mean_spm']:.1f} spm** ({lwt_u23_m['top25_mean_work_j']:.0f}–{lwt_open_m['top25_mean_work_j']:.0f} J/stroke), whereas `Open/Heavyweight` Men average **{hwt_u23_m['top25_mean_spm']:.1f}–{hwt_open_m['top25_mean_spm']:.1f} spm** while generating **{hwt_u23_m['top25_mean_work_j']:.0f}–{hwt_open_m['top25_mean_work_j']:.0f} J/stroke**.",
        f"2. **Within-Class Rate vs. Time Correlations & Age Confounding in Masters:** Across all {len(cat_df)} categories, `corr_spm_vs_time_r` spans **`{min(all_rs):+.3f}` to `{max(all_rs):+.3f}`** (and **`{min(open_u23_rs):+.3f}` to `{max(open_u23_rs):+.3f}`** across `Open/Senior` and `U23` categories). In competitive senior/collegiate cohorts (such as Open/U23 Lightweight Men at $r = {lwt_open_m['corr_spm_vs_time_r']}$ / ${lwt_u23_m['corr_spm_vs_time_r']}$ and Open/U23 Heavyweight Men at $r = {hwt_open_m['corr_spm_vs_time_r']}$ / ${hwt_u23_m['corr_spm_vs_time_r']}$), higher stroke rate correlates strongly with faster finish times. By contrast, in pooled `Masters` categories (which span ages 27 through 95+) and small novice `U15` heats, age and experience differences dominate finish times and attenuate the raw rate correlation.",
        "",
        "---",
        "",
        f"## 4. Finding 3: Quarter-by-Quarter Telemetry ($Q_1 \\to Q_4$, $n = {len(tel_df)}$)",
        "",
        "*(Note on Stratification: In the bottom two rows below, races are conditioned on their third-quarter split delta $Q_3 - Q_1$ to compare how stroke rate $R$ and Distance Per Stroke $\\text{DPS}$ evolve in even-paced pieces versus positive-split fades. The $Q_3 - Q_1$ split difference is the grouping criterion itself, while the resulting rate and $\\text{DPS}$ curves reflect physiological fatigue rather than a mechanical flywheel effect.)*",
        "",
        "![PM5 Telemetry Quarter-by-Quarter Stroke Rate and Split Decay](../data/charts/telemetry_quarters_pacing.svg)",
        "",
        "| Telemetry Cohort | Races ($n$) | $Q_1$ Rate | $Q_2$ Rate | $Q_3$ Rate | $Q_4$ Rate | $Q_1$ Split | $Q_3$ Split | $Q_3 - Q_1$ Delta | $Q_3 - Q_2$ DPS |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    for pr in pacing_summary_rows:
        q1_fmt = format_split(pr["q1_split_s"]) if pr["q1_split_s"] != "" else "-"
        q3_fmt = format_split(pr["q3_split_s"]) if pr["q3_split_s"] != "" else "-"
        decay_str = f"{pr['q3_minus_q1_split_s']:+.2f} s" if pr["q3_minus_q1_split_s"] != "" else "-"
        lines.append(
            f"| **{pr['cohort']}** | {pr['n_races']} | {pr['q1_spm']:.1f} spm | {pr['q2_spm']:.1f} spm | "
            f"{pr['q3_spm']:.1f} spm | **{pr['q4_spm']:.1f} spm** | {q1_fmt} | {q3_fmt} | **{decay_str}** | `{pr['q3_minus_q2_dps_m']:+.3f} m` |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 5. Reproducing the Pipeline & Running Verification Tests",
        "",
        "Run the complete data, evaluation, and test pipeline from the [`data/`](../data/) directory using `make`:",
        "",
        "```bash",
        "cd data",
        "make all        # Builds athlete_heights.csv, runs fetch_crashb.py, evaluate_crashb.py, and test_math.py",
        "make test       # Runs pytest / unittest mathematical and dataset integrity verification suite",
        "make evaluate   # Re-runs statistical evaluations and regenerates SVG charts in data/charts/",
        "make clean-raw  # Deletes git-ignored raw HTML/telemetry caches in data/raw/",
        "```",
        "",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote height evaluation summary to {out_height_csv}")
    print(f"Wrote category evaluation summary to {out_cat_csv}")
    print(f"Generated 4 SVG charts in {CHARTS_DIR}/")
    print(f"Wrote empirical analysis report to {report_path}")


if __name__ == "__main__":
    main()
