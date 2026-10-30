# Archived C.R.A.S.H.-B. Pipeline

**This code is no longer used.** Nothing in the main [`README.md`](../README.md) depends on it. It is kept as a record of the work.

## What it was for

It tried to test drag factor advice against real racing. It scraped C.R.A.S.H.-B. and 2019 World Rowing Indoor Championships results and race charts from Time-Team, matched rowers to public heights by name, and compared height with stroke rate and work per stroke.

## Why it is not used

* **The data has no drag factor.** Results and race charts record time, distance, speed and stroke rate. They do not record drag factor or drive length.
* **Splits cannot reveal the setting.** The monitor [accounts for damping](../docs/references.md#dudhia-the-physics-of-rowing), and [rowers can choose any drag factor](../docs/references.md#crash-b-sprints-faq).
* **A single sentence states the finding.** The main README records that the data has no drag factor. That does not need about 2,000 lines of code and a 173 MB cache.
* **The one analysis does not test drag factor.** It rests on 55 name-matched athletes and gives a wide, inconclusive result.
* **It adds privacy and accuracy risk.** It handles named people, its hashes of public names can be reversed with a name list, and some height matches may be the wrong person.

## Last results (2026-10-30)

| Item | Result |
| :--- | :--- |
| 2,000m results | 4,620 |
| Race charts | 400 |
| Rowers with a name-matched height | 67, across 83 starts |
| Open/heavyweight men, rate change per +10 cm of height | +2.74 spm (95% CI +0.32 to +5.17) |
| Same, with power held constant | +0.40 spm (95% CI −1.69 to +2.48) |
| Open/heavyweight women, rate change per +10 cm of height | +1.03 spm (95% CI −0.17 to +2.23) |
| Same, with power held constant | −0.51 spm (95% CI −2.08 to +1.05) |

These figures come from 33 men and 22 women, and they do not test drag factor. Do not use them to support any recommendation.

## Known problems

* **Heights are name matches, not confirmed identities.** The `verified_height_cm` column name is out of date. Matching uses sex, surname and fuzzy score, with no birth-year check.
* **The drive length estimate is unpublished.** `est_drive_length_m` (0.0078 × height − 0.08) has no source.
* **Some code is unused.** The catch-slip, flywheel, and Handle Drag Factor functions run only in self-checks and tests. Their inertia and sprocket values have no source.
* **Race charts are not a random sample.** The selection was made earlier and cannot be rebuilt from an empty cache.
* **CSV row order varies between runs.** The rows themselves do not change.
* **2021 is not parsed.** Time-Team hosts a [2021 results page](https://regatta.time-team.nl/crashb/2021/results/events.php). There is no 2024 page.
* **A full rebuild was not tested.** The last run used the local cache. Without it, `make fetch` scrapes over 1,000 pages.

## Running it

CSVs, charts and the report are git-ignored. With a local `raw/` cache:

```bash
cd data
make all    # Build heights, fetch results, evaluate, and test
make test   # Run the checks; tests that need outputs skip if they are missing
```

`make evaluate` writes the report to `crash-b-data.md`.

## Data sources

These are pipeline inputs, not recommendations. The Wikidata IDs, results pages and Olympic CSV link were checked. The roster pages and the Griffin (2018) citation were not.

[`fetch_crashb.py`](fetch_crashb.py) and [`build_athlete_heights.py`](build_athlete_heights.py) downloads race results, PM5 race charts, and athlete heights from the following public repositories and endpoints (caching raw downloads locally in git-ignored `raw/`):

### Time-Team Regatta Systems: C.R.A.S.H.-B. Sprints & WRIC Results / PM5 Telemetry
* **C.R.A.S.H.-B. Sprints Archives (2018–2020, 2022–2023, 2025–2026):**
  * [https://regatta.time-team.nl/crashb/2018](https://regatta.time-team.nl/crashb/2018)
  * [https://regatta.time-team.nl/crashb/2019](https://regatta.time-team.nl/crashb/2019)
  * [https://regatta.time-team.nl/crashb/2020](https://regatta.time-team.nl/crashb/2020)
  * [https://regatta.time-team.nl/crashb/2022](https://regatta.time-team.nl/crashb/2022)
  * [https://regatta.time-team.nl/crashb/2023](https://regatta.time-team.nl/crashb/2023)
  * [https://regatta.time-team.nl/crashb/2025](https://regatta.time-team.nl/crashb/2025)
  * [https://regatta.time-team.nl/crashb/2026](https://regatta.time-team.nl/crashb/2026)
* **World Rowing Indoor Championships (WRIC 2019):**
  * [https://regatta.time-team.nl/wric/2019](https://regatta.time-team.nl/wric/2019)
* **Summary:** Official Time-Team regatta result tables (500m, 1,000m, 1,500m, and 2,000m splits plus average stroke rate `spm`) and PM5 race charts (about one point per second) harvested by [`data/fetch_crashb.py`](fetch_crashb.py).

### Wikidata Query Service (SPARQL Endpoint): International & World Rowing Athlete Stature
* **SPARQL Endpoint:** [https://query.wikidata.org/sparql](https://query.wikidata.org/sparql)
* **Entities & Properties Queried:** Occupation rower ([`wd:Q13382576`](https://www.wikidata.org/wiki/Q13382576) via `wdt:P106`), World Rowing (FISA) athlete ID ([`wdt:P2091`](https://www.wikidata.org/wiki/Property:P2091)), physical stature/height ([`wdt:P2048`](https://www.wikidata.org/wiki/Property:P2048) normalized to centimeters), sex or gender ([`wdt:P21`](https://www.wikidata.org/wiki/Property:P21)), and multilingual labels/aliases (`rdfs:label`, `skos:altLabel`).
* **Summary:** Queried by [`data/build_athlete_heights.py`](build_athlete_heights.py) to obtain heights for international, Olympic, and World Rowing championship competitors.

### Olympic Rowing Anthropometric Dataset (Griffin / Olympedia via R4DS TidyTuesday)
* **Direct CSV Endpoint:** [https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-07-27/olympics.csv](https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-07-27/olympics.csv)
* **Underlying Compilation:** Griffin, R. H. (2018), *"120 years of Olympic history: athletes and results"*, compiled from historical Olympic biographical records (`sports-reference.com` / Olympedia).
* **Summary:** Filtered to `sport == "Rowing"` records with verified `height` (cm) and `weight` (kg) by [`data/build_athlete_heights.py`](build_athlete_heights.py).

### NCAA & IRA Collegiate Varsity Rowing Rosters (Sidearm Sports Archives)
* **University Athletics Roster Endpoints (2019–20 Season Archives):**
  * **Yale University** ([Men's Heavyweight](https://yalebulldogs.com/sports/mens-crew/roster/2019-20), [Women's Crew](https://yalebulldogs.com/sports/womens-crew/roster/2019-20))
  * **Brown University** ([Men's Crew](https://brownbears.com/sports/mens-crew/roster/2019-20), [Women's Crew](https://brownbears.com/sports/womens-crew/roster/2019-20))
  * **Princeton University** ([Men's Heavyweight](https://goprincetontigers.com/sports/mens-rowing/roster/2019-20), [Women's Open](https://goprincetontigers.com/sports/womens-rowing/roster/2019-20))
  * **Syracuse University** ([Women's Rowing](https://cuse.com/sports/rowing/roster/2019-20))
  * **Northeastern University** ([Men's Rowing](https://nuhuskies.com/sports/mens-rowing/roster/2019-20), [Women's Rowing](https://nuhuskies.com/sports/womens-rowing/roster/2019-20))
  * **Boston University** ([Men's Rowing](https://goterriers.com/sports/mens-rowing/roster/2019-20), [Women's Lightweight Rowing](https://goterriers.com/sports/womens-lightweight-rowing/roster/2019-20))
  * **Drexel University** ([Men's Rowing](https://drexeldragons.com/sports/mens-rowing/roster/2019-20), [Women's Rowing](https://drexeldragons.com/sports/womens-rowing/roster/2019-20))
  * **Mercyhurst University** ([Men's Rowing](https://hurstathletics.com/sports/mens-rowing/roster/2019-20), [Women's Rowing](https://hurstathletics.com/sports/womens-rowing/roster/2019-20))
* **Summary:** Parsed with `BeautifulSoup` and matched against regatta competitors via `rapidfuzz` token normalization (`rapidfuzz.fuzz.token_sort_ratio`, cutoff $\ge 90$) in [`data/build_athlete_heights.py`](build_athlete_heights.py).
