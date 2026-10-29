#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "beautifulsoup4",
#   "pandas",
# ]
# ///
"""
Download and parse C.R.A.S.H.-B. Sprints (2018-2020, 2022-2023, 2025-2026) and
World Rowing Indoor Championships (WRIC 2019) results and stroke-rate telemetry
from Time-Team using BeautifulSoup and pandas.

Note on Regatta Years:
  - 2021 C.R.A.S.H.-B. and 2024 C.R.A.S.H.-B. are not hosted on the Time-Team
    regatta server and are therefore not included.

Privacy & Git Hygiene:
  - Raw HTML/JSON downloads are cached in data/raw/ (excluded via .gitignore).
  - Athlete names are never stored in any output file; a pseudonymized SHA-256
    digest (`athlete_id`) is used strictly to join verified anthropometric records.
  - Produces pseudonymized summary CSVs in data/:
      * data/crashb_2k_summary.csv
      * data/crashb_quarter_telemetry.csv
"""

import csv
import hashlib
import json
import math
import re
import sys
import time
import unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from bs4 import BeautifulSoup
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "raw"

REGATTAS = [
    ("crashb", 2018, "https://regatta.time-team.nl/crashb/2018"),
    ("crashb", 2019, "https://regatta.time-team.nl/crashb/2019"),
    ("crashb", 2020, "https://regatta.time-team.nl/crashb/2020"),
    ("crashb", 2022, "https://regatta.time-team.nl/crashb/2022"),
    ("crashb", 2023, "https://regatta.time-team.nl/crashb/2023"),
    ("crashb", 2025, "https://regatta.time-team.nl/crashb/2025"),
    ("crashb", 2026, "https://regatta.time-team.nl/crashb/2026"),
    ("wric", 2019, "https://regatta.time-team.nl/wric/2019"),
]


def make_athlete_id(name: str) -> str:
    """Pseudonymized SHA-256 hash of normalized athlete name (12 hex chars)."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    norm = re.sub(r"[^a-z]", "", ascii_name.lower())
    return hashlib.sha256(("ergdrag:" + norm).encode("utf-8")).hexdigest()[:12]


def est_drive_len_from_height(height_cm: float) -> float:
    """
    Kleshnev BioRow anthropometric model: total ergometer reach L_total (m)
    as a function of verified rower stature H (cm).
    At H = 200 cm -> L ~ 1.48 m; H = 180 cm -> L ~ 1.324 m; H = 165 cm -> L ~ 1.207 m.
    """
    return round(0.0078 * height_cm - 0.08, 3)


def compute_2k_kinematics(finish_time_s: float, spm: float) -> dict:
    """
    Compute exact Concept2 2,000m kinematics and energetics from finish time
    (seconds) and average stroke rate R (strokes/min):
      - avg_split_500_s = finish_time_s / 4.0
      - avg_speed_ms    = 2000.0 / finish_time_s = 500.0 / avg_split_500_s
      - avg_watts       = 2.80 * v^3  (Dudhia / Concept2 cubic power law)
      - dps_m           = v * 60 / R  (Distance Per Stroke in meters)
      - work_per_stroke = P * 60 / R  (Mechanical Work per Stroke in Joules)
    """
    avg_split_500 = finish_time_s / 4.0
    avg_speed_ms = 2000.0 / finish_time_s
    watts = 2.80 * (avg_speed_ms ** 3)
    dps_m = avg_speed_ms * 60.0 / spm
    work_per_stroke_j = watts * 60.0 / spm
    return {
        "avg_split_500_s": avg_split_500,
        "avg_speed_ms": avg_speed_ms,
        "avg_watts": watts,
        "dps_m": dps_m,
        "work_per_stroke_j": work_per_stroke_j,
    }


def compute_quarter_dps(mean_speed_ms: float, mean_spm: float) -> float:
    """Compute Distance Per Stroke (meters) = v * (60 / R) for a race quarter."""
    return mean_speed_ms * 60.0 / mean_spm


def load_verified_heights() -> dict:
    path = BASE_DIR / "athlete_heights.csv"
    lookup = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                lookup[r["athlete_id"]] = float(r["height_cm"])
    return lookup


def fetch_url(url: str, cache_path: Path, retries: int = 3, allow_network: bool = True) -> str:
    if cache_path.exists() and cache_path.stat().st_size > 0:
        return cache_path.read_text(encoding="utf-8", errors="ignore")
    if not allow_network:
        return ""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ErgDragFactorsResearch/1.0)"},
    )
    for attempt in range(retries):
        try:
            time.sleep(0.1)  # Polite rate limit for uncached HTTP requests
            with urllib.request.urlopen(req, timeout=15) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
                cache_path.write_text(text, encoding="utf-8")
                return text
        except Exception:
            if attempt == retries - 1:
                return ""
    return ""


def parse_time_to_seconds(t_str: str):
    if not t_str:
        return None
    t_str = t_str.strip()
    m = re.match(r"^(?:(\d+):)?(\d{1,2}):(\d{2}\.\d+)$", t_str)
    if m:
        hrs = int(m.group(1) or 0)
        mins = int(m.group(2))
        secs = float(m.group(3))
        return hrs * 3600 + mins * 60 + secs
    m2 = re.match(r"^(\d+\.\d+)$", t_str)
    if m2:
        return float(m2.group(1))
    return None


def classify_event(event_code: str, event_desc: str, header_text: str, remarks: str = ""):
    code = event_code.strip()
    desc = event_desc.strip()
    hdr = header_text.strip()
    rem = remarks.strip()
    combined = f"{code} | {desc} | {hdr} | {rem}"

    dist_m = 2000
    m_dist = re.search(r"(\d+)\s*meter", hdr, re.IGNORECASE)
    if m_dist:
        dist_m = int(m_dist.group(1))
    if "500m" in combined.lower():
        dist_m = 500
    elif "minutes" in combined.lower() or "minute" in combined.lower():
        dist_m = 0

    is_relay = (
        "relay" in combined.lower()
        or "team" in combined.lower()
        or re.search(r"\b4\b", code) is not None
        or "mix" in code.lower()
    )

    is_para = bool(
        re.search(
            r"\b(PR1|PR2|PR3|LTA|TA|AS|FES|I1|I2|I3|I4|I5|I6|ID|VI|ARMS|TRUNK|II|PI|AK|SA|GD|RA)\b",
            combined.upper(),
        )
        or any(w in combined.lower() for w in ["adaptive", "para", "impaired", "disabled", "amputee"])
    )

    sex = "Unknown"
    if "mix" in code.lower() or "mixed" in desc.lower():
        sex = "Mixed"
    elif re.search(r"\b(womens|women's|women)\b", desc.lower()) or re.match(r"^(LW|W|FW|JLW|JW|YW)", code.upper()):
        sex = "W"
    elif re.search(r"\b(mens|men's|men)\b", desc.lower()) or re.match(r"^(LM|M|FM|JLM|JM|YM)", code.upper()):
        sex = "M"

    if "flyweight" in combined.lower() or re.match(r"^(FM|FW)\b", code.upper()):
        weight_class = "Flyweight"
    elif (
        "lightweight" in combined.lower()
        or "lwt" in combined.lower()
        or re.match(r"^(LM|LW|JLM|JLW)\b", code.upper())
        or re.match(r"^(LM|LW|JLM|JLW)(\d|[CS]$)", code.upper())
    ):
        weight_class = "Lightweight"
    else:
        weight_class = "Open/Heavyweight"

    u_code = code.upper()
    u_desc = desc.upper()
    if "U15" in u_code or "U15" in u_desc or "YOUTH" in u_desc or re.match(r"^Y[MW]", u_code):
        age_cat = "U15/Youth"
    elif "U17" in u_code or "U17" in u_desc:
        age_cat = "U17"
    elif (
        "U19" in u_code
        or "U19" in u_desc
        or "JUNIOR" in u_desc
        or re.match(r"^(JL?[MW]|L?[MW]J)\b", u_code)
        or re.match(r"^JL?[MW]\d+", u_code)
    ):
        age_cat = "U19/Junior"
    elif (
        "U23" in u_code
        or "U23" in u_desc
        or "COLLEGE" in u_desc
        or "UNDER 23" in u_desc
        or re.match(r"^L?[MW][CS]$", u_code)
    ):
        age_cat = "U23"
    elif (
        "MASTER" in u_desc
        or "VETERAN" in u_desc
        or "SENIOR MEN (AGE 40" in u_desc
        or "SENIOR WOMEN (AGE 40" in u_desc
        or re.search(r"\b\d{2}\s*-\s*\d{2}\b", u_code)
        or re.search(r"\b(27|30|36|40|43|50|55|60|65|70|75|80|85|90|95)\+?\b", u_code)
        or re.match(r"^L?[MW](27|30|40|50|55|60|65|70|75|80|85|90|95)\+?$", u_code)
        or re.match(r"^L?[MW]\s+(AA|[A-N])\b", u_code)
    ):
        age_cat = "Masters"
    else:
        age_cat = "Open/Senior"

    return {
        "sex": sex,
        "weight_class": weight_class,
        "age_category": age_cat,
        "distance_m": dist_m,
        "is_relay": is_relay,
        "is_para": is_para,
    }


def parse_events_index(events_html: str) -> list:
    """Parse Time-Team events.php index page using BeautifulSoup."""
    if not events_html:
        return []
    soup = BeautifulSoup(events_html, "html.parser")
    events = []
    idx = 0
    for tr in soup.select("table.timeteam tr"):
        classes = tr.get("class") or []
        if "smallrow" in classes:
            continue
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        a_tag = tds[1].find("a", href=True)
        if not a_tag or not a_tag["href"].startswith("e"):
            continue
        idx += 1
        ev_no = tds[0].get_text(strip=True) or f"{idx:03d}"
        nxt = tr.find_next_sibling("tr")
        desc = ""
        if nxt and "smallrow" in (nxt.get("class") or []):
            desc = nxt.get_text(" ", strip=True)
        events.append({
            "file": a_tag["href"],
            "no": ev_no,
            "code": tds[1].get_text(strip=True),
            "entries": tds[2].get_text(strip=True),
            "remarks": tds[3].get_text(strip=True),
            "desc": desc,
        })
    return events


def parse_event_page(html: str, regatta: str, year: int, event_info: dict, verified_heights: dict):
    """Parse an individual event results page using BeautifulSoup."""
    rows = []
    telemetry_targets = []
    if not html:
        return rows, telemetry_targets

    soup = BeautifulSoup(html, "html.parser")
    h2 = soup.find("h2")
    header_text = h2.get_text(" ", strip=True) if h2 else ""
    base_meta = classify_event(
        event_info["code"],
        event_info["desc"],
        header_text,
        event_info.get("remarks", ""),
    )

    if base_meta["distance_m"] != 2000 or base_meta["is_relay"] or base_meta["is_para"] or base_meta["sex"] not in ("M", "W"):
        return rows, telemetry_targets

    table = soup.find("table", class_="timeteam")
    if not table:
        return rows, telemetry_targets

    # Inspect thead to detect whether an extra `event` column is present (e.g., CRASH-B 2022)
    thead = table.find("thead")
    th_texts = [th.get_text(" ", strip=True).lower() for th in thead.find_all("th")] if thead else []
    # Require 500m, 1000m, 1500m headers to confirm a 2,000m table layout
    if th_texts and not any("500m" in t for t in th_texts):
        return rows, telemetry_targets

    has_event_col = len(th_texts) > 3 and th_texts[3] == "event"
    col_offset = 1 if has_event_col else 0
    min_cols = 11 + col_offset

    for tbody in table.find_all("tbody"):
        trs = tbody.find_all("tr", recursive=False)
        if len(trs) < 2:
            continue

        tds1 = trs[0].find_all("td", recursive=False)
        tds2 = trs[1].find_all("td", recursive=False)
        if len(tds1) < min_cols or len(tds2) < min_cols:
            continue

        row1_texts = [td.get_text(" ", strip=True).replace("\xa0", " ") for td in tds1]
        row2_texts = [td.get_text(" ", strip=True).replace("\xa0", " ") for td in tds2]

        joined_r1 = " ".join(row1_texts).lower()
        if any(w in joined_r1 for w in ["did not start", "did not finish", "excluded", "disqualified"]):
            continue

        pos_str = row1_texts[0].rstrip(".")
        pos = int(pos_str) if pos_str.isdigit() else None
        raw_name = row1_texts[2]
        if not raw_name:
            continue

        # In 2022, individual rowers have their specific event code in col 3 (e.g. LM vs M, LM A vs M A)
        row_code = row1_texts[3] if (has_event_col and row1_texts[3]) else event_info["code"]
        meta = classify_event(row_code, event_info["desc"], header_text, event_info.get("remarks", ""))
        if meta["is_para"] or meta["is_relay"] or meta["sex"] not in ("M", "W"):
            continue

        athlete_id = make_athlete_id(raw_name)

        erg_a = trs[0].find("a", href=re.compile(r"\.\./erg/"))
        erg_file = erg_a["href"].split("../erg/")[-1] if erg_a else ""

        spm = None
        for txt in reversed(row2_texts):
            m_spm = re.search(r"(\d+(?:\.\d+)?)\s*spm", txt, re.IGNORECASE)
            if m_spm:
                spm = float(m_spm.group(1))
                break

        idx_500 = 3 + col_offset
        idx_1000 = 5 + col_offset
        idx_1500 = 7 + col_offset
        idx_2000 = 9 + col_offset

        t_500 = parse_time_to_seconds(row1_texts[idx_500])
        t_1000 = parse_time_to_seconds(row1_texts[idx_1000])
        t_1500 = parse_time_to_seconds(row1_texts[idx_1500])
        t_2000 = parse_time_to_seconds(row1_texts[idx_2000])

        s_q1 = parse_time_to_seconds(row2_texts[idx_500])
        s_q2 = parse_time_to_seconds(row2_texts[idx_1000])
        s_q3 = parse_time_to_seconds(row2_texts[idx_1500])
        s_q4 = parse_time_to_seconds(row2_texts[idx_2000])

        if t_2000 is None or t_2000 <= 0 or spm is None or spm <= 0:
            continue

        # Sanity check quarter splits (must be positive and < finish_time_s)
        if any(s is not None and (s <= 0 or s >= t_2000) for s in (s_q1, s_q2, s_q3, s_q4)):
            s_q1 = s_q2 = s_q3 = s_q4 = None

        kin = compute_2k_kinematics(t_2000, spm)
        verified_h = verified_heights.get(athlete_id)
        est_l = est_drive_len_from_height(verified_h) if verified_h is not None else ""

        row_dict = {
            "athlete_id": athlete_id,
            "regatta": regatta,
            "year": year,
            "event_code": row_code,
            "sex": meta["sex"],
            "weight_class": meta["weight_class"],
            "age_category": meta["age_category"],
            "position": pos,
            "time_500_s": round(t_500, 2) if t_500 else None,
            "time_1000_s": round(t_1000, 2) if t_1000 else None,
            "time_1500_s": round(t_1500, 2) if t_1500 else None,
            "finish_time_s": round(t_2000, 2),
            "split_q1_s": round(s_q1, 2) if s_q1 else None,
            "split_q2_s": round(s_q2, 2) if s_q2 else None,
            "split_q3_s": round(s_q3, 2) if s_q3 else None,
            "split_q4_s": round(s_q4, 2) if s_q4 else None,
            "avg_split_500_s": round(kin["avg_split_500_s"], 2),
            "avg_speed_ms": round(kin["avg_speed_ms"], 4),
            "avg_watts": round(kin["avg_watts"], 1),
            "avg_spm": spm,
            "dps_m": round(kin["dps_m"], 3),
            "work_per_stroke_j": round(kin["work_per_stroke_j"], 1),
            "verified_height_cm": round(verified_h, 1) if verified_h is not None else "",
            "est_drive_length_m": est_l,
        }
        rows.append(row_dict)

        if erg_file:
            telemetry_targets.append({
                "regatta": regatta,
                "year": year,
                "erg_file": erg_file,
                "summary_row": row_dict,
            })

    return rows, telemetry_targets


def parse_erg_telemetry(html: str, target: dict):
    """Extract Q1-Q4 stroke rate, speed, and DPS from PM5 race chart JSON."""
    if not html:
        return None
    m = re.search(r"var\s+data\s*=\s*(\[\{.*?\}\]);", html, re.DOTALL)
    if not m:
        return None
    try:
        pts = json.loads(m.group(1))
    except Exception:
        return None

    quarters = {1: [], 2: [], 3: [], 4: []}
    start_rates = []
    sprint_rates = []

    for p in pts:
        d = p.get("distance")
        r = p.get("rate")
        v = p.get("speed")
        if d is None or r is None or v is None or r <= 10 or v <= 1.0:
            continue
        if d <= 100:
            start_rates.append(r)
        if d >= 1750:
            sprint_rates.append(r)
        if 0 < d <= 500:
            quarters[1].append((r, v))
        elif 500 < d <= 1000:
            quarters[2].append((r, v))
        elif 1000 < d <= 1500:
            quarters[3].append((r, v))
        elif 1500 < d <= 2000:
            quarters[4].append((r, v))

    if any(len(quarters[q]) < 3 for q in (1, 2, 3, 4)):
        return None

    sr = target["summary_row"]
    q_spm = {}
    q_dps = {}
    for q in (1, 2, 3, 4):
        rates = [x[0] for x in quarters[q]]
        spds = [x[1] for x in quarters[q]]
        mean_r = sum(rates) / len(rates)
        mean_v = sum(spds) / len(spds)
        q_spm[q] = round(mean_r, 2)
        q_dps[q] = round(compute_quarter_dps(mean_v, mean_r), 3)

    return {
        "athlete_id": sr["athlete_id"],
        "regatta": sr["regatta"],
        "year": sr["year"],
        "sex": sr["sex"],
        "weight_class": sr["weight_class"],
        "age_category": sr["age_category"],
        "finish_time_s": sr["finish_time_s"],
        "avg_watts": sr["avg_watts"],
        "avg_spm": sr["avg_spm"],
        "verified_height_cm": sr["verified_height_cm"],
        "est_drive_length_m": sr["est_drive_length_m"],
        "q1_spm": q_spm[1],
        "q2_spm": q_spm[2],
        "q3_spm": q_spm[3],
        "q4_spm": q_spm[4],
        "start_100m_spm": round(sum(start_rates) / len(start_rates), 2) if start_rates else "",
        "sprint_250m_spm": round(sum(sprint_rates) / len(sprint_rates), 2) if sprint_rates else "",
        "q1_dps_m": q_dps[1],
        "q2_dps_m": q_dps[2],
        "q3_dps_m": q_dps[3],
        "q4_dps_m": q_dps[4],
        "split_q1_s": sr["split_q1_s"],
        "split_q2_s": sr["split_q2_s"],
        "split_q3_s": sr["split_q3_s"],
        "split_q4_s": sr["split_q4_s"],
    }


def verify_math() -> None:
    """
    Self-contained mathematical verification of all equations and transformations
    in fetch_crashb.py.
    """
    assert math.isclose(est_drive_len_from_height(200.0), 1.480, abs_tol=1e-9)
    assert math.isclose(est_drive_len_from_height(180.0), 1.324, abs_tol=1e-9)
    assert math.isclose(est_drive_len_from_height(165.0), 1.207, abs_tol=1e-9)

    k_400 = compute_2k_kinematics(400.0, 35.0)
    assert math.isclose(k_400["avg_split_500_s"], 100.0, rel_tol=1e-12)
    assert math.isclose(k_400["avg_speed_ms"], 5.0, rel_tol=1e-12)
    assert math.isclose(k_400["avg_watts"], 350.0, rel_tol=1e-12)
    assert math.isclose(k_400["work_per_stroke_j"], 600.0, rel_tol=1e-12)
    assert math.isclose(k_400["dps_m"], 300.0 / 35.0, rel_tol=1e-12)

    # Verify Masters letter code classification ("M D", "W AA", "LM A")
    assert classify_event("M D", "Mens Masters D", "[111] M D 2000 meter")["age_category"] == "Masters"
    assert classify_event("LM A", "Mens Masters A", "[036] M A 2000 meter")["weight_class"] == "Lightweight"
    assert classify_event("W U19", "Womens U19", "[039] W U19 500 meter", "500m")["distance_m"] == 500


def main():
    verify_math()
    if "--test" in sys.argv:
        print("fetch_crashb.py: all mathematical assertions passed.")
        return

    verified_heights = load_verified_heights()
    all_rows = []
    all_telemetry_targets = []

    for regatta, year, base_url in REGATTAS:
        reg_dir = RAW_DIR / f"{regatta}_{year}"
        events_html = fetch_url(f"{base_url}/results/events.php", reg_dir / "events.html")
        if not events_html:
            raise RuntimeError(f"Could not load events.html for {regatta} {year}")

        events = parse_events_index(events_html)
        print(f"Parsing {len(events)} events for {regatta.upper()} {year}...")

        def process_event(ev):
            url = f"{base_url}/results/{ev['file']}"
            cpath = reg_dir / "results" / ev["file"]
            html = fetch_url(url, cpath)
            return parse_event_page(html, regatta, year, ev, verified_heights)

        regatta_rows = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            futs = [pool.submit(process_event, ev) for ev in events]
            for fut in as_completed(futs):
                r_list, t_list = fut.result()
                regatta_rows.extend(r_list)
                all_telemetry_targets.extend(t_list)

        if not regatta_rows:
            raise RuntimeError(f"Zero 2,000m records parsed for {regatta} {year} — check HTML parser!")
        print(f"  -> {len(regatta_rows)} individual 2,000m records parsed for {regatta.upper()} {year}")
        all_rows.extend(regatta_rows)

    all_rows.sort(key=lambda r: (r["regatta"], r["year"], r["sex"], r["weight_class"], r["finish_time_s"]))

    summary_csv = BASE_DIR / "crashb_2k_summary.csv"
    pd.DataFrame(all_rows).to_csv(summary_csv, index=False)

    matched_verified = sum(1 for r in all_rows if r["verified_height_cm"] != "")
    print(f"Saved {len(all_rows)} pseudonymized 2,000m records to {summary_csv}")
    print(f"  Records matched to verified roster heights: {matched_verified}")

    # Parse cached stroke-by-stroke PM5 race charts (or fetch up to 400 if uncached)
    url_map = {(r, y): u for r, y, u in REGATTAS}
    cached_targets = [
        t for t in all_telemetry_targets
        if (RAW_DIR / f"{t['regatta']}_{t['year']}" / "erg" / t["erg_file"]).exists()
    ]
    targets_to_parse = cached_targets if cached_targets else all_telemetry_targets[:400]
    print(f"Parsing {len(targets_to_parse)} stroke-by-stroke PM5 race charts...")

    def fetch_telemetry(t):
        base_url = url_map[(t["regatta"], t["year"])]
        reg_dir = RAW_DIR / f"{t['regatta']}_{t['year']}"
        url = f"{base_url}/erg/{t['erg_file']}"
        cpath = reg_dir / "erg" / t["erg_file"]
        html = fetch_url(url, cpath)
        return parse_erg_telemetry(html, t)

    telemetry_rows = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = [pool.submit(fetch_telemetry, t) for t in targets_to_parse]
        for fut in as_completed(futs):
            res = fut.result()
            if res is not None:
                telemetry_rows.append(res)

    telemetry_rows.sort(key=lambda r: (r["sex"], r["weight_class"], r["finish_time_s"]))
    telemetry_csv = BASE_DIR / "crashb_quarter_telemetry.csv"
    if telemetry_rows:
        pd.DataFrame(telemetry_rows).to_csv(telemetry_csv, index=False)

    print(f"Saved {len(telemetry_rows)} pseudonymized quarter-by-quarter telemetry records to {telemetry_csv}")


if __name__ == "__main__":
    main()
