#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "beautifulsoup4",
#   "pandas",
#   "rapidfuzz",
# ]
# ///
"""
Download verified rower height data from public sources (Wikidata SPARQL API,
Olympic Rowing Dataset, and NCAA/IRA Collegiate Varsity Rosters), match athlete
names using `rapidfuzz` token normalization/matching, and write the pseudonymized
lookup table (`data/athlete_heights.csv`).

No athlete names or heights are hardcoded in this script; all raw source files
are cached in `data/raw/heights/` (excluded from Git via `.gitignore`).
"""

import gzip
import hashlib
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup
import pandas as pd
from rapidfuzz import fuzz, process, utils

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "raw"
HEIGHTS_RAW_DIR = RAW_DIR / "heights"

WIKIDATA_SPARQL_QUERY = """
SELECT DISTINCT ?personLabel ?altLabel ?height ?sex WHERE {
  { ?person wdt:P106 wd:Q13382576 . }
  UNION
  { ?person wdt:P2091 ?fisaId . }
  ?person p:P2048/psv:P2048 ?heightNode .
  ?heightNode wikibase:quantityAmount ?val ;
              wikibase:quantityUnit ?unit .
  OPTIONAL { ?person wdt:P21 ?sex . }
  OPTIONAL { ?person skos:altLabel ?altLabel . FILTER(LANG(?altLabel) IN ("en", "de", "fr", "nl", "pl", "cs", "hu")) }
  BIND(
    IF(?unit = wd:Q11573, ?val * 100,
    IF(?unit = wd:Q174728, ?val,
    IF(?unit = wd:Q218593, ?val * 2.54, 0))) AS ?height
  )
  FILTER(?height >= 150 && ?height <= 220)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,de,fr,nl,es,it,pl,cs,da,no,sv,fi,hu,ro,el,uk". }
}
"""

OLYMPICS_CSV_URL = (
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/"
    "data/2021/2021-07-27/olympics.csv"
)

COLLEGIATE_ROSTER_URLS = [
    ("M", "Open/Heavyweight", "https://yalebulldogs.com/sports/mens-crew/roster/2019-20"),
    ("W", "Open/Heavyweight", "https://yalebulldogs.com/sports/womens-crew/roster/2019-20"),
    ("M", "Open/Heavyweight", "https://brownbears.com/sports/mens-crew/roster/2019-20"),
    ("W", "Open/Heavyweight", "https://brownbears.com/sports/womens-crew/roster/2019-20"),
    ("M", "Open/Heavyweight", "https://goprincetontigers.com/sports/mens-rowing/roster/2019-20"),
    ("W", "Open/Heavyweight", "https://goprincetontigers.com/sports/womens-rowing/roster/2019-20"),
    ("W", "Open/Heavyweight", "https://cuse.com/sports/rowing/roster/2019-20"),
    ("M", "Open/Heavyweight", "https://nuhuskies.com/sports/mens-rowing/roster/2019-20"),
    ("W", "Open/Heavyweight", "https://nuhuskies.com/sports/womens-rowing/roster/2019-20"),
    ("M", "Open/Heavyweight", "https://goterriers.com/sports/mens-rowing/roster/2019-20"),
    ("W", "Lightweight", "https://goterriers.com/sports/womens-lightweight-rowing/roster/2019-20"),
    ("M", "Open/Heavyweight", "https://drexeldragons.com/sports/mens-rowing/roster/2019-20"),
    ("W", "Open/Heavyweight", "https://drexeldragons.com/sports/womens-rowing/roster/2019-20"),
    ("M", "Open/Heavyweight", "https://hurstathletics.com/sports/mens-rowing/roster/2019-20"),
    ("W", "Open/Heavyweight", "https://hurstathletics.com/sports/womens-rowing/roster/2019-20"),
]


def normalize_name(name: str) -> str:
    """Normalize and tokenize a rower name using Unicode NFKD + rapidfuzz.utils.default_process."""
    if not name or not isinstance(name, str):
        return ""
    cleaned = re.sub(r"\(.*?\)|\"[^\"]*\"|\x27[^\x27]*\x27", " ", name).replace("•", " ")
    folded = unicodedata.normalize("NFKD", cleaned).encode("ascii", "ignore").decode("ascii")
    return utils.default_process(folded)


def make_athlete_id(name: str) -> str:
    """Pseudonymized SHA-256 hash of normalized athlete name (12 hex chars)."""
    ascii_name = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode("ascii")
    norm = re.sub(r"[^a-z]", "", ascii_name.lower())
    return hashlib.sha256(("ergdrag:" + norm).encode("utf-8")).hexdigest()[:12]


def est_drive_len_from_height(height_cm: float) -> float:
    """Internal, unpublished estimate: L_est = 0.0078 * H_cm - 0.08 (m)."""
    return round(0.0078 * height_cm - 0.08, 3)


def download_reference_sources() -> dict[str, dict[str, tuple[float, str]]]:
    """
    Download and parse public rower height sources into `data/raw/heights/`.
    Returns `ref_by_sex[sex][normalized_name] = (height_cm, weight_class)`.
    """
    HEIGHTS_RAW_DIR.mkdir(parents=True, exist_ok=True)
    ref_by_sex: dict[str, dict[str, tuple[float, str]]] = {"M": {}, "W": {}}

    def add_entry(raw_name: str, sex: str, height_cm: float, weight_class: str = "Open/Heavyweight") -> None:
        norm = normalize_name(raw_name)
        if len(norm.split()) >= 2 and 150.0 <= height_cm <= 220.0 and sex in ("M", "W"):
            ref_by_sex[sex][norm] = (round(float(height_cm), 1), weight_class)

    # 1. Olympic Rowing Dataset
    tt_cache = HEIGHTS_RAW_DIR / "olympics_rowers.csv"
    if not tt_cache.exists():
        df_tt = pd.read_csv(OLYMPICS_CSV_URL)
        df_tt = df_tt[(df_tt["sport"] == "Rowing") & (df_tt["height"].notna())][
            ["name", "sex", "height", "weight"]
        ].drop_duplicates()
        df_tt.to_csv(tt_cache, index=False)

    df_tt = pd.read_csv(tt_cache)
    for _, row in df_tt.iterrows():
        sex = "M" if row["sex"] == "M" else "W"
        h = float(row["height"])
        w = float(row["weight"]) if pd.notna(row["weight"]) else None
        wc = "Open/Heavyweight"
        if w is not None and ((sex == "M" and w <= 75.0) or (sex == "W" and w <= 61.5)):
            wc = "Lightweight"
        add_entry(str(row["name"]), sex, h, wc)

    # 2. Wikidata SPARQL API (Rowers & World Rowing ID holders with height P2048)
    wd_cache = HEIGHTS_RAW_DIR / "wikidata_rowers.json"
    if not wd_cache.exists():
        url = "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(WIKIDATA_SPARQL_QUERY)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ErgDragFactorsResearch/1.0", "Accept-Encoding": "gzip"},
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read()
            if resp.info().get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            wd_cache.write_bytes(raw)

    wd_data = json.loads(wd_cache.read_text(encoding="utf-8"))
    for b in wd_data.get("results", {}).get("bindings", []):
        h = float(b["height"]["value"])
        sex_uri = b.get("sex", {}).get("value", "")
        sex = "M" if sex_uri.endswith("Q6581097") else ("W" if sex_uri.endswith("Q6581072") else "")
        if not sex:
            continue
        names = [b.get("personLabel", {}).get("value", "")]
        if "altLabel" in b:
            names.extend([x.strip() for x in b["altLabel"]["value"].split(",")])
        for nm in names:
            prev_wc = ref_by_sex[sex].get(normalize_name(nm), (None, "Open/Heavyweight"))[1]
            add_entry(nm, sex, h, prev_wc)

    # 3. NCAA / IRA Collegiate Varsity Rowing Rosters
    for sex, wc, url in COLLEGIATE_ROSTER_URLS:
        slug = re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")
        cpath = HEIGHTS_RAW_DIR / f"roster_{slug}.html"
        if not cpath.exists():
            try:
                time.sleep(0.1)
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    cpath.write_bytes(resp.read())
            except Exception:
                continue
        if not cpath.exists():
            continue
        soup = BeautifulSoup(cpath.read_text(encoding="utf-8", errors="ignore"), "html.parser")
        for li in soup.select("li.sidearm-roster-player, div.s-person-card, tr"):
            text = li.get_text(" ", strip=True)
            m_h = re.search(r"\b([56])(?:-|\x27\s*)([0-9]{1,2})(?:\x22|\b)", text)
            if not m_h:
                continue
            ft, inch = int(m_h.group(1)), int(m_h.group(2))
            if inch > 11:
                continue
            h_cm = round((ft * 12 + inch) * 2.54, 1)
            a = li.select_one(
                'div.sidearm-roster-player-name a, h3 a, td.sidearm-table-player-name a, a[href*="/roster/"]'
            )
            if a:
                nm = a.get_text(" ", strip=True)
                if nm and " " in nm and len(nm) < 40:
                    add_entry(nm, sex, h_cm, wc)

    return ref_by_sex


def collect_regatta_competitors() -> list[tuple[str, str, str]]:
    """
    Extract unique `(raw_name, sex, weight_class)` entries from cached Time-Team
    regatta HTML pages in `data/raw/` (excluding U15/U17 youth events).
    """
    import fetch_crashb

    seen = {}
    for reg, yr, _url in fetch_crashb.REGATTAS:
        ev_index_path = RAW_DIR / f"{reg}_{yr}" / "events.html"
        if not ev_index_path.exists():
            continue
        ev_html = ev_index_path.read_text(encoding="utf-8", errors="ignore")
        for ev in fetch_crashb.parse_events_index(ev_html):
            res_path = RAW_DIR / f"{reg}_{yr}" / "results" / ev["file"]
            if not res_path.exists():
                continue
            soup = BeautifulSoup(res_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
            h2 = soup.find("h2")
            hdr = h2.get_text(" ", strip=True) if h2 else ""
            base_meta = fetch_crashb.classify_event(ev["code"], ev["desc"], hdr, ev.get("remarks", ""))
            if (
                base_meta["distance_m"] != 2000
                or base_meta["is_relay"]
                or base_meta["is_para"]
                or base_meta["sex"] not in ("M", "W")
            ):
                continue
            table = soup.find("table", class_="timeteam")
            if not table:
                continue
            thead = table.find("thead")
            th_texts = [th.get_text(" ", strip=True).lower() for th in thead.find_all("th")] if thead else []
            if th_texts and not any("500m" in t for t in th_texts):
                continue
            has_event_col = len(th_texts) > 3 and th_texts[3] == "event"
            for tbody in table.find_all("tbody"):
                trs = tbody.find_all("tr", recursive=False)
                if len(trs) < 2:
                    continue
                tds1 = trs[0].find_all("td", recursive=False)
                if len(tds1) < 11:
                    continue
                r1 = [td.get_text(" ", strip=True).replace("\xa0", " ") for td in tds1]
                raw_name = r1[2]
                if not raw_name:
                    continue
                row_code = r1[3] if (has_event_col and r1[3]) else ev["code"]
                meta = fetch_crashb.classify_event(row_code, ev["desc"], hdr, ev.get("remarks", ""))
                if meta["age_category"] in ("U15/Youth", "U17") or meta["sex"] not in ("M", "W"):
                    continue
                aid = make_athlete_id(raw_name)
                seen[aid] = (raw_name, meta["sex"], meta["weight_class"])
    return list(seen.values())


def main() -> None:
    ref_by_sex = download_reference_sources()
    competitors = collect_regatta_competitors()

    # Index reference names by (sex, last_token) so rapidfuzz matches within same surname/sex
    ref_indexed: dict[tuple[str, str], list[str]] = {}
    for sex in ("M", "W"):
        for norm_name in ref_by_sex[sex]:
            toks = norm_name.split()
            if toks:
                ref_indexed.setdefault((sex, toks[-1]), []).append(norm_name)

    matched_rows = []
    seen_aids = set()
    for raw_name, sex, comp_wc in competitors:
        norm = normalize_name(raw_name)
        toks = norm.split()
        if len(toks) < 2:
            continue
        candidates = ref_indexed.get((sex, toks[-1]), [])
        if not candidates:
            continue
        match = process.extractOne(
            norm,
            candidates,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=90.0,
        )
        if not match:
            continue
        matched_norm = match[0]
        height_cm, _ref_wc = ref_by_sex[sex][matched_norm]
        aid = make_athlete_id(raw_name)
        if aid in seen_aids:
            continue
        seen_aids.add(aid)
        matched_rows.append({
            "athlete_id": aid,
            "sex": sex,
            "weight_class": comp_wc,
            "height_cm": round(height_cm, 1),
            "height_in": round(height_cm / 2.54, 1),
            "est_drive_length_m": est_drive_len_from_height(height_cm),
        })

    df = pd.DataFrame(matched_rows).sort_values(
        by=["sex", "height_cm", "athlete_id"],
        ascending=[True, False, True],
    )
    out_path = BASE_DIR / "athlete_heights.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} dynamically matched & pseudonymized height records to {out_path}")


if __name__ == "__main__":
    main()
