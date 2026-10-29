#!/usr/bin/env python3
"""
Download and parse C.R.A.S.H.-B. Sprints (2018-2026) and World Rowing Indoor
Championships (WRIC 2019) results and stroke-rate telemetry from Time-Team.

Privacy & Git Hygiene:
  - Raw HTML/JSON downloads are cached in data/raw/ (excluded via .gitignore).
  - Athlete names are never stored in any output file; a one-way SHA-256 digest
    (`athlete_id`) is used strictly to join verified anthropometric records.
  - Produces clean, anonymized summary CSVs in data/:
      * data/crashb_2k_summary.csv
      * data/crashb_quarter_telemetry.csv
"""

import csv
import hashlib
import html as html_lib
import json
import re
import unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

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

# Standard anthropometric stature baselines (cm) by (sex, weight_class, age_category)
# Used when an athlete is not in the verified roster height lookup table.
CATEGORY_HEIGHT_CM = {
    ("M", "Open/Heavyweight", "Open/Senior"): 192.0,
    ("M", "Open/Heavyweight", "U23"): 191.0,
    ("M", "Open/Heavyweight", "U19/Junior"): 186.0,
    ("M", "Open/Heavyweight", "U17"): 182.0,
    ("M", "Open/Heavyweight", "U15/Youth"): 174.0,
    ("M", "Open/Heavyweight", "Masters"): 185.0,
    ("M", "Lightweight", "Open/Senior"): 179.0,
    ("M", "Lightweight", "U23"): 179.0,
    ("M", "Lightweight", "U19/Junior"): 176.0,
    ("M", "Lightweight", "U17"): 173.0,
    ("M", "Lightweight", "Masters"): 177.0,
    ("M", "Flyweight", "Open/Senior"): 172.0,
    ("W", "Open/Heavyweight", "Open/Senior"): 179.0,
    ("W", "Open/Heavyweight", "U23"): 178.0,
    ("W", "Open/Heavyweight", "U19/Junior"): 173.0,
    ("W", "Open/Heavyweight", "U17"): 170.0,
    ("W", "Open/Heavyweight", "U15/Youth"): 164.0,
    ("W", "Open/Heavyweight", "Masters"): 171.0,
    ("W", "Lightweight", "Open/Senior"): 167.0,
    ("W", "Lightweight", "U23"): 167.0,
    ("W", "Lightweight", "U19/Junior"): 164.0,
    ("W", "Lightweight", "U17"): 162.0,
    ("W", "Lightweight", "Masters"): 164.0,
    ("W", "Flyweight", "Open/Senior"): 160.0,
}


def make_athlete_id(name: str) -> str:
    """One-way SHA-256 hash of normalized athlete name (12 hex chars)."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    norm = re.sub(r"[^a-z]", "", ascii_name.lower())
    return hashlib.sha256(("ergdrag:" + norm).encode("utf-8")).hexdigest()[:12]


def est_drive_len_from_height(height_cm: float) -> float:
    """
    Kleshnev BioRow anthropometric model: total ergometer reach L_total (m)
    as a function of rower stature H (cm).
    At H = 200 cm -> L ~ 1.48 m; H = 180 cm -> L ~ 1.32 m; H = 165 cm -> L ~ 1.21 m.
    """
    return round(0.0078 * height_cm - 0.08, 3)


def load_verified_heights() -> dict:
    path = BASE_DIR / "athlete_heights.csv"
    lookup = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                lookup[r["athlete_id"]] = float(r["height_cm"])
    return lookup


def fetch_url(url: str, cache_path: Path, retries: int = 3) -> str:
    if cache_path.exists() and cache_path.stat().st_size > 0:
        return cache_path.read_text(encoding="utf-8", errors="ignore")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ErgDragFactorsResearch/1.0)"},
    )
    for attempt in range(retries):
        try:
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


def classify_event(event_code: str, event_desc: str, header_text: str):
    code = event_code.strip()
    desc = event_desc.strip()
    hdr = header_text.strip()
    combined = f"{code} | {desc} | {hdr}"

    dist_m = 2000
    m_dist = re.search(r"(\d+)\s*meter", hdr, re.IGNORECASE)
    if m_dist:
        dist_m = int(m_dist.group(1))
    elif "500m" in desc or "500m" in code:
        dist_m = 500
    elif "minutes" in desc.lower() or "minute" in hdr.lower():
        dist_m = 0

    is_relay = (
        "relay" in desc.lower()
        or "team" in desc.lower()
        or re.search(r"\b4\b", code) is not None
        or "mix" in code.lower()
    )

    is_para = bool(
        re.search(
            r"\b(PR1|PR2|PR3|LTA|TA|AS|FES|I1|I2|I3|I4|I5|I6|ID|VI|ARMS|TRUNK)\b",
            combined.upper(),
        )
        or any(w in desc.lower() for w in ["adaptive", "para", "impaired", "disabled", "amputee"])
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
        or re.match(r"^(LM|LW|JLM|JLW)", code.upper())
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
    elif "U23" in u_code or "U23" in u_desc or "COLLEGE" in u_desc or "UNDER 23" in u_desc:
        age_cat = "U23"
    elif (
        "MASTER" in u_desc
        or "VETERAN" in u_desc
        or "SENIOR MEN (AGE 40" in u_desc
        or "SENIOR WOMEN (AGE 40" in u_desc
        or re.search(r"\b\d{2}\s*-\s*\d{2}\b", u_code)
        or re.search(r"\b(30|36|40|43|50|55|60|65|70|75|80|85|90|95)\b", u_code)
        or re.match(r"^L?[MW](30|40|50|55|60|65|70|75|80|85|90|95)$", u_code)
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


def strip_tags(s: str) -> str:
    return html_lib.unescape(re.sub(r"<[^>]+>", "", s)).replace("\xa0", " ").strip()


def parse_event_page(html: str, regatta: str, year: int, event_info: dict, verified_heights: dict):
    rows = []
    telemetry_targets = []
    if not html:
        return rows, telemetry_targets

    h2_m = re.search(r"<h2>(.*?)</h2>", html, re.DOTALL)
    header_text = strip_tags(h2_m.group(1)) if h2_m else ""
    meta = classify_event(event_info["code"], event_info["desc"], header_text)

    # Filter strictly to individual 2,000m non-para races for the 2k summary
    if meta["distance_m"] != 2000 or meta["is_relay"] or meta["is_para"] or meta["sex"] not in ("M", "W"):
        return rows, telemetry_targets

    tbodies = re.findall(r"<tbody id='([^']+)'>(.*?)</tbody>", html, re.DOTALL)
    for tbody_id, tbody_html in tbodies:
        trs = re.findall(r"<tr[^>]*>(.*?)</tr>", tbody_html, re.DOTALL)
        if len(trs) < 2:
            continue

        tds1 = re.findall(r"<td[^>]*>(.*?)</td>", trs[0], re.DOTALL)
        tds2 = re.findall(r"<td[^>]*>(.*?)</td>", trs[1], re.DOTALL)
        if len(tds1) < 11 or len(tds2) < 11:
            continue

        pos_str = strip_tags(tds1[0]).rstrip(".")
        pos = int(pos_str) if pos_str.isdigit() else None
        raw_name = strip_tags(tds1[2])
        if not raw_name:
            continue

        # Immediately hash athlete name -> 12-char SHA-256 hex ID
        athlete_id = make_athlete_id(raw_name)

        erg_m = re.search(r"href='\.\./erg/([^']+)'", trs[0])
        erg_file = erg_m.group(1) if erg_m else ""

        row1_texts = [strip_tags(td) for td in tds1]
        row2_texts = [strip_tags(td) for td in tds2]

        joined_r1 = " ".join(row1_texts).lower()
        if any(w in joined_r1 for w in ["did not start", "did not finish", "excluded", "disqualified"]):
            continue

        spm = None
        for txt in reversed(row2_texts):
            m_spm = re.search(r"(\d+(?:\.\d+)?)\s*spm", txt, re.IGNORECASE)
            if m_spm:
                spm = float(m_spm.group(1))
                break

        t_500 = parse_time_to_seconds(row1_texts[3])
        t_1000 = parse_time_to_seconds(row1_texts[5])
        t_1500 = parse_time_to_seconds(row1_texts[7])
        t_2000 = parse_time_to_seconds(row1_texts[9])

        s_q1 = parse_time_to_seconds(row2_texts[3])
        s_q2 = parse_time_to_seconds(row2_texts[5])
        s_q3 = parse_time_to_seconds(row2_texts[7])
        s_q4 = parse_time_to_seconds(row2_texts[9])

        if t_2000 is None or t_2000 <= 0 or spm is None or spm <= 0:
            continue

        avg_split_500 = t_2000 / 4.0
        avg_speed_ms = 2000.0 / t_2000
        watts = 2.80 * (avg_speed_ms ** 3)
        dps_m = avg_speed_ms * 60.0 / spm
        work_per_stroke_j = watts * 60.0 / spm

        verified_h = verified_heights.get(athlete_id)
        cat_h = CATEGORY_HEIGHT_CM.get(
            (meta["sex"], meta["weight_class"], meta["age_category"]),
            182.0 if meta["sex"] == "M" else 170.0,
        )
        effective_h = verified_h if verified_h is not None else cat_h
        est_l = est_drive_len_from_height(effective_h)

        row_dict = {
            "athlete_id": athlete_id,
            "regatta": regatta,
            "year": year,
            "event_code": event_info["code"],
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
            "avg_split_500_s": round(avg_split_500, 2),
            "avg_speed_ms": round(avg_speed_ms, 4),
            "avg_watts": round(watts, 1),
            "avg_spm": spm,
            "dps_m": round(dps_m, 3),
            "work_per_stroke_j": round(work_per_stroke_j, 1),
            "verified_height_cm": round(verified_h, 1) if verified_h is not None else "",
            "est_height_cm": round(effective_h, 1),
            "est_drive_length_m": est_l,
        }
        rows.append(row_dict)

        # Queue high-resolution race chart telemetry for verified-height athletes,
        # Open/Senior, U23, Lightweight/Flyweight, and podium finishers
        if erg_file and (
            verified_h is not None
            or meta["age_category"] in ("Open/Senior", "U23")
            or meta["weight_class"] in ("Lightweight", "Flyweight")
            or (pos is not None and pos <= 3)
        ):
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
    q_spd = {}
    q_dps = {}
    for q in (1, 2, 3, 4):
        rates = [x[0] for x in quarters[q]]
        spds = [x[1] for x in quarters[q]]
        mean_r = sum(rates) / len(rates)
        mean_v = sum(spds) / len(spds)
        q_spm[q] = round(mean_r, 2)
        q_spd[q] = round(mean_v, 4)
        q_dps[q] = round(mean_v * 60.0 / mean_r, 3)

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
        "est_height_cm": sr["est_height_cm"],
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


def main():
    verified_heights = load_verified_heights()
    all_rows = []
    all_telemetry_targets = []

    for regatta, year, base_url in REGATTAS:
        reg_dir = RAW_DIR / f"{regatta}_{year}"
        events_html = fetch_url(f"{base_url}/results/events.php", reg_dir / "events.html")
        if not events_html:
            print(f"[WARN] Could not fetch {regatta} {year}")
            continue

        pattern = re.compile(
            r"<tr class='(?:even|odd)'><td>(.*?)</td>"
            r"<td><a href='(e[0-9a-f\-]+\.php)'>([^<]+)</a></td><td>([^<]*)</td><td>([^<]*)</td></tr>"
            r"\s*<tr class='smallrow (?:even|odd)'><td></td><td colspan='4'>([^<]*)</td></tr>",
            re.DOTALL,
        )
        events = []
        for idx, m in enumerate(pattern.finditer(events_html), start=1):
            ev_no = strip_tags(m.group(1)) or f"{idx:03d}"
            events.append({
                "file": m.group(2),
                "no": ev_no,
                "code": strip_tags(m.group(3)),
                "entries": strip_tags(m.group(4)),
                "remarks": strip_tags(m.group(5)),
                "desc": strip_tags(m.group(6)),
            })

        print(f"Parsing {len(events)} events for {regatta.upper()} {year}...")

        def process_event(ev):
            url = f"{base_url}/results/{ev['file']}"
            cpath = reg_dir / "results" / ev["file"]
            html = fetch_url(url, cpath)
            return parse_event_page(html, regatta, year, ev, verified_heights)

        with ThreadPoolExecutor(max_workers=16) as pool:
            futs = [pool.submit(process_event, ev) for ev in events]
            for fut in as_completed(futs):
                r_list, t_list = fut.result()
                all_rows.extend(r_list)
                all_telemetry_targets.extend(t_list)

    all_rows.sort(key=lambda r: (r["regatta"], r["year"], r["sex"], r["weight_class"], r["finish_time_s"]))

    summary_csv = BASE_DIR / "crashb_2k_summary.csv"
    if all_rows:
        with summary_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_rows)

    matched_verified = sum(1 for r in all_rows if r["verified_height_cm"] != "")
    print(f"Saved {len(all_rows)} anonymized 2,000m records to {summary_csv}")
    print(f"  Records matched to verified roster heights: {matched_verified}")

    # Now fetch/parse high-resolution PM5 telemetry for prioritized targets
    # Prioritize verified-height athletes first, plus up to 350 stratified championship pieces
    prioritized = sorted(
        all_telemetry_targets,
        key=lambda t: (
            0 if t["summary_row"]["verified_height_cm"] != "" else 1,
            0 if t["summary_row"]["age_category"] in ("Open/Senior", "U23") else 1,
            t["summary_row"]["finish_time_s"],
        ),
    )[:400]

    print(f"Fetching/parsing {len(prioritized)} stroke-by-stroke PM5 race charts...")
    url_map = {(r, y): u for r, y, u in REGATTAS}

    def fetch_telemetry(t):
        base_url = url_map[(t["regatta"], t["year"])]
        reg_dir = RAW_DIR / f"{t['regatta']}_{t['year']}"
        url = f"{base_url}/erg/{t['erg_file']}"
        cpath = reg_dir / "erg" / t["erg_file"]
        html = fetch_url(url, cpath)
        return parse_erg_telemetry(html, t)

    telemetry_rows = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = [pool.submit(fetch_telemetry, t) for t in prioritized]
        for fut in as_completed(futs):
            res = fut.result()
            if res is not None:
                telemetry_rows.append(res)

    telemetry_rows.sort(key=lambda r: (r["sex"], r["weight_class"], r["finish_time_s"]))
    telemetry_csv = BASE_DIR / "crashb_quarter_telemetry.csv"
    if telemetry_rows:
        with telemetry_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(telemetry_rows[0].keys()))
            writer.writeheader()
            writer.writerows(telemetry_rows)

    print(f"Saved {len(telemetry_rows)} anonymized quarter-by-quarter telemetry records to {telemetry_csv}")


if __name__ == "__main__":
    main()
