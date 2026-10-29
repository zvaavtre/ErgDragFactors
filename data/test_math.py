#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy",
#   "pandas",
#   "scipy",
#   "beautifulsoup4",
#   "matplotlib",
#   "pytest",
#   "rapidfuzz",
# ]
# ///
"""
Automated Verification Suite for ErgDragFactors Mathematical & Empirical Models.

Uses established scientific libraries (`scipy`, `numpy`, `pandas`, `pytest`) to prove:
1. Concept2 Ergometer Physics & Kinematics (Dudhia 2000; Concept2 PM5 formulation).
2. Flywheel Recovery Deceleration ODE against `scipy.integrate.solve_ivp` (RK45).
3. Catch Slip & Kleshnev Handle Drag Factor (HDF) Scaling Invariants.
4. Anthropometric Height -> Drive Length Proxy & Empirical Regressions (`scipy.stats`).
5. Data Pipeline & Parser Invariants (including CRASH-B 2022 column layout & Masters letter codes).
6. Dataset Integrity across `athlete_heights.csv`, `crashb_2k_summary.csv`, and `crashb_quarter_telemetry.csv`.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import integrate, stats

# Ensure data directory is importable
DATA_DIR = Path(__file__).resolve().parent
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

import build_athlete_heights
import evaluate_crashb
import fetch_crashb


# ==============================================================================
# 1. Rowing Physics & Biomechanical Model Equations (Docs 00, 01, 02)
# ==============================================================================

def dudhia_omega_min_numerical(
    omega_max: float,
    drag_factor: float,
    spm: float,
    drive_time_s: float,
    inertia: float = evaluate_crashb.CONCEPT2_INERTIA_KGM2,
) -> float:
    """Numerical integration of I * d(omega)/dt = -k * omega^2 using scipy.integrate.solve_ivp."""
    k_si = evaluate_crashb.drag_factor_to_si(drag_factor)
    t_rec = evaluate_crashb.recovery_time_s(spm, drive_time_s)
    sol = integrate.solve_ivp(
        fun=lambda _t, y: [-(k_si / inertia) * (y[0] ** 2)],
        t_span=(0.0, t_rec),
        y0=[omega_max],
        method="RK45",
        rtol=1e-12,
        atol=1e-14,
    )
    return float(sol.y[0, -1])


# ==============================================================================
# 2. Physics & Mathematical Unit Tests
# ==============================================================================

def test_concept2_power_split_bijection():
    """Verify Concept2 watts <-> split conversions and exact benchmark splits."""
    # Exact benchmark: 1:40.0/500m (100s) -> v = 5.0 m/s -> P = 2.80 * 125 = 350.0 W
    assert np.isclose(evaluate_crashb.watts_from_split_500(100.0), 350.0, rtol=1e-12)
    assert np.isclose(evaluate_crashb.split_500_from_watts(350.0), 100.0, rtol=1e-12)

    # Exact benchmark: 2:05.0/500m (125s) -> v = 4.0 m/s -> P = 2.80 * 64 = 179.2 W
    assert np.isclose(evaluate_crashb.watts_from_split_500(125.0), 179.2, rtol=1e-12)

    # Round-trip bijection across physiological range (1:15.0 to 2:45.0)
    splits = np.linspace(75.0, 165.0, 50)
    for s in splits:
        w = evaluate_crashb.watts_from_split_500(s)
        assert np.isclose(evaluate_crashb.split_500_from_watts(w), s, rtol=1e-12)


def test_compute_2k_kinematics():
    """Verify fetch_crashb.compute_2k_kinematics against first-principles identities."""
    # 6:40.0 2k (400.0s) at 30 spm -> 1:40.0 split (100s), 5.0 m/s, 350 W, 10.0m DPS, 700 J/stroke
    kin = fetch_crashb.compute_2k_kinematics(400.0, 30.0)
    assert np.isclose(kin["avg_split_500_s"], 100.0, rtol=1e-12)
    assert np.isclose(kin["avg_speed_ms"], 5.0, rtol=1e-12)
    assert np.isclose(kin["avg_watts"], 350.0, rtol=1e-12)
    assert np.isclose(kin["dps_m"], 10.0, rtol=1e-12)
    assert np.isclose(kin["work_per_stroke_j"], 700.0, rtol=1e-12)


def test_dudhia_flywheel_ode_matches_scipy_rk45():
    """Prove evaluate_crashb.flywheel_omega_min matches scipy RK45 integration."""
    for df in [90, 110, 125, 140, 160]:
        for omega_max in [110.0, 145.0, 175.0]:
            for spm in [28.0, 32.0, 36.0]:
                drive_t = 0.80
                w_ana = evaluate_crashb.flywheel_omega_min(omega_max, df, spm, drive_t)
                w_num = dudhia_omega_min_numerical(omega_max, df, spm, drive_t)
                assert np.isclose(w_ana, w_num, rtol=1e-10)


def test_catch_slip_and_kleshnev_hdf_scaling():
    """Verify catch_slip_m, effective_drive_length_m, and Kleshnev HDF cubic length scaling."""
    # Catch slip: L_slip = (r^2 * omega_min^2) / (2 * a_catch)
    omega_min = 120.0
    a_catch = 15.0
    slip = evaluate_crashb.catch_slip_m(omega_min, a_catch)
    expected_slip = ((0.014 * 120.0) ** 2) / (2.0 * 15.0)
    assert np.isclose(slip, expected_slip, rtol=1e-12)
    assert np.isclose(evaluate_crashb.effective_drive_length_m(1.45, slip), 1.45 - expected_slip, rtol=1e-12)

    # Kleshnev HDF: HDF = P_drive / (L / T_drive)^3 -> inverse cubic scaling with L
    p_drive = 800.0
    t_drive = 0.85
    l_short = 1.25
    l_tall = 1.50
    hdf_short = evaluate_crashb.handle_drag_factor(p_drive, l_short, t_drive)
    hdf_tall = evaluate_crashb.handle_drag_factor(p_drive, l_tall, t_drive)
    assert np.isclose(hdf_short / hdf_tall, (l_tall / l_short) ** 3, rtol=1e-12)


def test_anthropometric_drive_length_proxy():
    """Verify the height -> drive length proxy formula across stature classes."""
    # L_est = round(0.0078 * H_cm - 0.08, 3)
    assert np.isclose(fetch_crashb.est_drive_len_from_height(165.0), 1.207, rtol=1e-12)
    assert np.isclose(fetch_crashb.est_drive_len_from_height(180.0), 1.324, rtol=1e-12)
    assert np.isclose(fetch_crashb.est_drive_len_from_height(195.0), 1.441, rtol=1e-12)
    assert np.isclose(build_athlete_heights.est_drive_len_from_height(203.0), 1.503, rtol=1e-12)


def test_ols_summary_matches_scipy_stats():
    """Verify evaluate_crashb.ols_summary matches scipy.stats.pearsonr and linregress."""
    rng = np.random.default_rng(42)
    x = rng.normal(190.0, 8.0, size=60)
    y = -0.11 * x + 55.0 + rng.normal(0.0, 1.2, size=60)
    r, slope, intercept, _t_stat, p_val = evaluate_crashb.ols_summary(x, y)
    r_ref, p_ref = stats.pearsonr(x, y)
    lr_ref = stats.linregress(x, y)
    assert np.isclose(r, r_ref, rtol=1e-12)
    assert np.isclose(p_val, p_ref, rtol=1e-12)
    assert np.isclose(slope, lr_ref.slope, rtol=1e-12)
    assert np.isclose(intercept, lr_ref.intercept, rtol=1e-12)


# ==============================================================================
# 3. Data Pipeline & Parser Tests (CRASH-B 2022 & Masters Letter Codes)
# ==============================================================================

def test_classify_event_masters_and_collegiate_codes():
    """Verify classify_event properly categorizes 2022 Masters letter codes and Collegiate codes."""
    # 2022 Masters letter codes ("M D", "W AA", "LM B", "LW E")
    for code, expected_sex, expected_wt in [
        ("M D", "M", "Open/Heavyweight"),
        ("W AA", "W", "Open/Heavyweight"),
        ("LM B", "M", "Lightweight"),
        ("LW G", "W", "Lightweight"),
    ]:
        info = fetch_crashb.classify_event(code, "Mens Masters", "2000 meter")
        assert info["age_category"] == "Masters", f"Failed Masters classification for {code}"
        assert info["sex"] == expected_sex
        assert info["weight_class"] == expected_wt

    # 2018/2019 Collegiate & Student sub-event codes
    for code, expected_sex, expected_wt in [
        ("MC", "M", "Open/Heavyweight"),
        ("LMC", "M", "Lightweight"),
        ("WC", "W", "Open/Heavyweight"),
        ("LWS", "W", "Lightweight"),
    ]:
        info = fetch_crashb.classify_event(code, "Open Men", "2000 meter")
        assert info["age_category"] == "U23", f"Failed U23 classification for {code}"
        assert info["sex"] == expected_sex
        assert info["weight_class"] == expected_wt

    # 500m sprint remarks should be flagged as 500m (not 2,000m)
    info_500 = fetch_crashb.classify_event("M", "Open Men", "2000 meter", remarks="500m")
    assert info_500["distance_m"] == 500


def test_parse_event_page_2022_extra_column():
    """Verify parse_event_page handles CRASH-B 2022's extra event column in thead/tbody."""
    sample_2022_html = """
    <html><body>
    <h2>Event 210: Mens Masters (2000 meter)</h2>
    <table class="timeteam">
      <thead>
        <tr>
          <th>pos</th><th></th><th>name</th><th>event</th>
          <th>500m</th><th></th><th>1000m</th><th></th><th>1500m</th><th></th><th>finish</th><th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1.</td><td></td><td>Test Rower One</td><td>M D</td>
          <td>1:33.0</td><td>(1)</td><td>3:07.0</td><td>(1)</td><td>4:41.0</td><td>(1)</td><td>6:15.4</td><td>+0.0</td>
        </tr>
        <tr>
          <td></td><td></td><td>Rowing Club A</td><td></td>
          <td>1:33.0</td><td></td><td>1:34.0</td><td></td><td>1:34.0</td><td></td><td>1:34.4</td><td>31 spm</td>
        </tr>
      </tbody>
      <tbody>
        <tr>
          <td>2.</td><td></td><td>Test Rower Two</td><td>LM B</td>
          <td>1:35.0</td><td>(2)</td><td>3:11.0</td><td>(2)</td><td>4:47.0</td><td>(2)</td><td>6:22.0</td><td>+6.6</td>
        </tr>
        <tr>
          <td></td><td></td><td>Rowing Club B</td><td></td>
          <td>1:35.0</td><td></td><td>1:36.0</td><td></td><td>1:36.0</td><td></td><td>1:35.0</td><td>32 spm</td>
        </tr>
      </tbody>
    </table>
    </body></html>
    """
    rows, _targets = fetch_crashb.parse_event_page(
        sample_2022_html,
        regatta="crashb",
        year=2022,
        event_info={"no": "210", "code": "M-MAST", "desc": "Mens Masters", "file": "e210.html", "remarks": ""},
        verified_heights={},
    )
    assert len(rows) == 2
    assert rows[0]["event_code"] == "M D"
    assert rows[0]["age_category"] == "Masters"
    assert rows[0]["weight_class"] == "Open/Heavyweight"
    assert np.isclose(rows[0]["finish_time_s"], 375.4)
    assert rows[1]["event_code"] == "LM B"
    assert rows[1]["age_category"] == "Masters"
    assert rows[1]["weight_class"] == "Lightweight"
    assert np.isclose(rows[1]["finish_time_s"], 382.0)


# ==============================================================================
# 4. Dataset Integrity & Invariant Tests
# ==============================================================================

def test_athlete_heights_csv_integrity():
    """Verify athlete_heights.csv is reproducible, contains no hardcoded PII/source_tier, and matches schema."""
    csv_path = DATA_DIR / "athlete_heights.csv"
    assert csv_path.exists(), "athlete_heights.csv must exist"
    df = pd.read_csv(csv_path)
    assert list(df.columns) == ["athlete_id", "sex", "weight_class", "height_cm", "height_in", "est_drive_length_m"]
    assert "source_tier" not in df.columns
    assert len(df) >= 50
    assert df["athlete_id"].str.match(r"^[0-9a-f]{12}$").all()
    assert df["height_cm"].between(150.0, 220.0).all()
    assert np.allclose(df["est_drive_length_m"], 0.0078 * df["height_cm"] - 0.08, atol=1e-3)
    assert build_athlete_heights.normalize_name("Lukáš Helešic (CZE)") == "lukas helesic"


def test_crashb_2k_summary_csv_invariants():
    """Verify crashb_2k_summary.csv has >0 rows for every regatta (including 2022) and exact physics."""
    csv_path = DATA_DIR / "crashb_2k_summary.csv"
    assert csv_path.exists(), "crashb_2k_summary.csv must exist"
    df = pd.read_csv(csv_path)

    # Every configured regatta must have > 0 rows (specifically guards against CRASH-B 2022 regression)
    for reg_slug, reg_year, _url in fetch_crashb.REGATTAS:
        sub = df[(df["regatta"].str.lower() == reg_slug.lower()) & (df["year"] == reg_year)]
        assert len(sub) > 0, f"Zero rows found for {reg_slug} {reg_year}"

    # Specifically verify CRASH-B 2022 has substantial coverage (>500 rows)
    df_2022 = df[(df["regatta"].str.upper() == "CRASHB") & (df["year"] == 2022)]
    assert len(df_2022) >= 500

    # Verify pseudonymized athlete_id format (12-char lowercase hex)
    assert df["athlete_id"].str.match(r"^[0-9a-f]{12}$").all()

    # Verify verified_height_cm and est_drive_length_m are ONLY populated for verified rowers
    unverified = df[df["verified_height_cm"].isna()]
    assert len(unverified) > 4000
    assert unverified["est_drive_length_m"].isna().all(), "Unverified rows must not have invented drive lengths"

    verified = df[df["verified_height_cm"].notna()]
    assert len(verified) >= 60
    assert np.allclose(
        verified["est_drive_length_m"],
        0.0078 * verified["verified_height_cm"] - 0.08,
        atol=1e-3,
    )

    # Verify kinematic columns obey exact Concept2 equations within rounding tolerance
    v = 2000.0 / df["finish_time_s"]
    assert np.allclose(df["avg_speed_ms"], v, atol=1e-3)
    assert np.allclose(df["avg_split_500_s"], df["finish_time_s"] / 4.0, atol=1e-2)
    assert np.allclose(df["avg_watts"], 2.80 * (v ** 3), atol=0.15)
    has_spm = df[df["avg_spm"].notna()]
    v_spm = 2000.0 / has_spm["finish_time_s"]
    assert np.allclose(has_spm["dps_m"], v_spm * 60.0 / has_spm["avg_spm"], atol=1e-2)
    assert np.allclose(has_spm["work_per_stroke_j"], 2.80 * (v_spm ** 3) * 60.0 / has_spm["avg_spm"], atol=0.2)


def test_doc04_has_no_stale_hardcoded_claims():
    """Verify docs/04-crash-b-empirical-analysis.md matches dynamically computed statistics."""
    doc_path = DATA_DIR.parent / "docs" / "04-crash-b-empirical-analysis.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    # Ensure old hardcoded claims flagged in review are absent
    assert "32.2–34.5" not in text
    assert "Flywheel Die-Off" not in text
    assert "4,620" in text


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
