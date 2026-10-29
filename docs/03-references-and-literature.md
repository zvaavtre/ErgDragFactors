# Reference Material & Annotated Bibliography

Complete breakdown of the primary academic papers, physics derivations, biomechanical newsletters, and manufacturer documentation referenced for modeling the Concept2 flywheel, drag factor, stroke length, and fatigue pacing during a 2,000m test.

---

## 1. Flywheel Physics & Differential Equations (The Mechanical Model)

### Anu Dudhia (Oxford): The Physics of Rowing
* **Source:** Oxford University Atmosphere, Ocean & Planetary Physics – *The Physics of Rowing: Ergometers*
* **Direct Link:** [http://eodg.atm.ox.ac.uk/user/dudhia/rowing/physics/ergometer.html](http://eodg.atm.ox.ac.uk/user/dudhia/rowing/physics/ergometer.html)
* **Main Physics of Rowing Index:** [https://www.atm.ox.ac.uk/rowing/physics/](https://www.atm.ox.ac.uk/rowing/physics/)
* **Summary:** The canonical mathematical derivation of the Concept2 flywheel. Derives the equation of motion for the rotating cage ($I \frac{d\omega}{dt} + k\omega^2 = \tau$), how the PM monitor measures the **Drag Factor** ($k$) during the unpowered recovery phase ($\left(\frac{d\omega}{dt}\right)_{\text{rec}} = -\frac{k}{I}\omega^2$), the Concept2 flywheel's moment of inertia ($I \approx 0.1001\text{ kg}\cdot\text{m}^2$), the exact sprocketed clutch engagement boundary (where handle velocity must exceed $r\omega$ to engage the flywheel, creating "catch slip"), and how power scales with the cube of velocity ($P = 2.80 / \text{pace}^3$).

### Concept2: Calculating Power and Pace
* **Source:** Concept2 Technical Note – *Calculating Power and Pace*
* **Direct Link:** [https://www.concept2.com/training/watts-calculator](https://www.concept2.com/training/watts-calculator)
* **Summary:** Defines the conversion equation between 500m split pace and mechanical power in Watts ($\text{Watts} = 2.80 / \text{pace}^3$).

---

## 2. Rowing Biomechanics: Handle Drag Factor (HDF), Catch Slip & Stroke Length

### Valery Kleshnev (BioRow): Handle Drag Factor
* **Source:** Dr. Valery Kleshnev (BioRow) – *Rowing Biomechanics Newsletter (RBN 2011/01)*
* **RBN 2011/01 (Handle Drag Factor):** [http://www.biorow.com/index.php?route=information/news/news&news_id=25](http://www.biorow.com/index.php?route=information/news/news&news_id=25)
* **BioRow Main Archive:** [http://www.biorow.com](http://www.biorow.com)
* **Summary:** Introduces the **Handle Drag Factor** ($\text{HDF} = \frac{P}{V_{h.\text{av}}^3} = \frac{P}{(L/T_d)^3}$), which relates average power ($P$), drive length ($L$), and drive time ($T_d$). Proves that on the water, HDF scales with rower weight and boat class, whereas on a Concept2 ergometer, resistance is independent of athlete weight unless manually adjusted via the damper.

### Valery Kleshnev and Carlos Dinares: On-Water vs. Ergometer Drag Factors
* **Source:** *Row2k Series: Biomechanics of On-Water vs. Ergometer Drag Factors*
* **Direct Link:** [https://www.row2k.com/features/567/Rowing-Biomechanics--Adjusting-Erg-Drag-Factor-to-Mimic-Feel-of-Boat/](https://www.row2k.com/features/567/Rowing-Biomechanics--Adjusting-Erg-Drag-Factor-to-Mimic-Feel-of-Boat/)
* **Summary:** Maps specific Concept2 drag factors against athlete body weight, boat class, and effective stroke length, and explains why heavy drag factors distort handle velocity curves compared to on-water shells.

### Valery Kleshnev: The Biomechanics of Rowing (2016 / 2020)
* **Source:** Book, The Crowood Press — 1st Ed., 2016 (`ISBN-13: 978-1785001338`); Revised 2nd Ed., 2020 (`ISBN-13: 978-1785007774`)
* **Summary:** Contains the longitudinal database of elite 2,000m telemetry, detailing how stroke length ($L$) naturally contracts as stroke rate ($R$) increases, and defines the **Catch Factor** and **Rowing Style Factor (RSF)** across different drag loads.

---

## 3. Peer-Reviewed Sports Science Studies on 2,000m Ergometer Drag Factor

### Kane et al. (2008 & 2013): Effects of Drag Factor and Stroke Resistance on Rowing Physiology & Economy
* **Source (2008):** Kane, D. A., Jensen, R. L., Williams, S. E., & Watts, P. B. (2008) – *"Effects of drag factor on physiological aspects of rowing"* (*International Journal of Sports Medicine*, 29(5), 390–394)
* **PubMed Link (2008):** [https://pubmed.ncbi.nlm.nih.gov/18401809/](https://pubmed.ncbi.nlm.nih.gov/18401809/)
* **Source (2013):** Kane, D. A., MacKenzie, S. J., Jensen, R. L., & Watts, P. B. (2013) – *"Effects of stroke resistance on rowing economy in club rowers post-season"* (*International Journal of Sports Medicine*, 34(2), 131–137)
* **PubMed Link (2013):** [https://pubmed.ncbi.nlm.nih.gov/22895868/](https://pubmed.ncbi.nlm.nih.gov/22895868/)
* **Summary:** Examines physiological responses ($\dot{V}\text{O}_2$, ventilation $\dot{V}_E$, blood lactate, heart rate, stroke rate, and rowing economy) across low (100) vs. high (150) drag factors on a Concept2 ergometer. Demonstrates that lower drag factors elicit significantly higher stroke rates and maximal ventilation, whereas higher drag factors increase stroke impulse and gross economy at the cost of higher muscular force per stroke.

### Cerasola et al. (2017): Drag Factor on Rowing Ergometer During 2000-m Performance
* **Source:** Cerasola, D., Cataldo, A., Bianco, A., Zangla, D., Capranica, L., & Traina, M. (*Kinesiologia Slovenica*, Vol. 23, Issue 2, pp. 15–21, 2017) – *"Drag factor on rowing ergometer during 2000-m performance in young rowers"*
* **Journal Archive:** [https://www.kinsi.si/](https://www.kinsi.si/)
* **Summary:** Evaluates 2,000m ergometer time-trial performance and stroke rate across low (110), intermediate (130), and high (150) drag factor settings, demonstrating that intermediate drag factors (~130) optimize 2,000m finish times ($419.1\text{ s}$ vs. $435.0\text{ s}$ at DF 110 and $433.7\text{ s}$ at DF 150) while stroke rate decreases monotonically as drag factor rises.

### Ingham et al. (2002): Determinants of 2000m Rowing Ergometer Performance
* **Source:** Ingham, S. A., Whyte, G. P., Jones, K., & Nevill, A. M. (2002) – *"Determinants of 2,000 m rowing ergometer performance in elite rowers"* (*European Journal of Applied Physiology*, 88(3), 243–246)
* **PubMed Link:** [https://pubmed.ncbi.nlm.nih.gov/12458367/](https://pubmed.ncbi.nlm.nih.gov/12458367/)
* **Summary:** Establishes the allometric scaling and force-velocity models predicting 2,000m ergometer performance from lean body mass, stroke length/leverage (sitting height and arm span), maximal power ($W_{\text{max}}$), and power at $\dot{V}\text{O}_{2\text{max}}$.

### Soper and Hume (2004): Towards an Ideal Rowing Technique for Performance
* **Source:** Soper, C., & Hume, P. A. (2004) – *"Towards an ideal rowing technique for performance: The contributions from biomechanics"* (*Sports Medicine*, 34(12), 825–848)
* **PubMed Link:** [https://pubmed.ncbi.nlm.nih.gov/15462614/](https://pubmed.ncbi.nlm.nih.gov/15462614/)
* **Summary:** Reviews the biomechanical literature on lumbar shear forces, peak handle force, and effective drive length under different ergometer resistance settings.

---

## 4. Concept2 Official Documentation & Telemetry Guides

### Concept2: Damper Setting 101 and Explaining Drag Factor
* **Damper Setting 101:** [https://www.concept2.com/training/articles/damper-setting-101](https://www.concept2.com/training/articles/damper-setting-101)
* **Explaining Drag Factor:** [https://www.concept2.com/training/articles/explaining-drag-factor](https://www.concept2.com/training/articles/explaining-drag-factor)
* **Summary:** Official engineering explanation of how the PM5 calculates drag factor on each recovery phase to self-calibrate for air density, altitude, and cage dust, and why damper settings 1–10 are merely air-intake vent positions.

### Concept2: ErgData Stroke Metrics (Drive Length, Drive Time, Force)
* **Direct Link:** [https://www.concept2.com/ergdata](https://www.concept2.com/ergdata)
* **Summary:** Explains how the PM5 sensor measures `Drive Length` (in meters), `Drive Speed`, and `Peak Force` vs. `Average Force` per stroke.

---

## 5. Championship Regatta Rules & National Federation Testing Protocols

### C.R.A.S.H.-B. Sprints: Official Drag Factor FAQ & "The Charley Butt Rule"
* **Official FAQ (*What drag factor do I have to use?*):** [http://www.crash-b.org/faq/what-drag-factor-do-i-have-to-use/](http://www.crash-b.org/faq/what-drag-factor-do-i-have-to-use/)
* **Official Regatta Rules:** [http://www.crash-b.org/2024-regatta/rules/](http://www.crash-b.org/2024-regatta/rules/)
* **Summary:** Official C.R.A.S.H.-B. Sprints (and World Rowing Indoor Championships) rules **do not mandate a fixed drag factor range (such as 130–140)**. Competitors may set the damper/drag factor to **any value they choose** before the race begins, but under the **"Charley Butt Rule"** are strictly prohibited from changing or adjusting the damper setting once the race has started (doing so results in immediate disqualification).

### National Federation 2,000m Testing Protocols (Where Mandated 125–140 / 130 Standards Originate)
While open indoor regattas like C.R.A.S.H.-B. allow free pre-race damper selection, national team selection and pathway testing protocols mandate specific category drag factors on the PM5 monitor so scores are standardized across athletes:
* **British Rowing (*Safety Alert: Setting Up Your C2 Rowing Machine*, 2018):** [https://www.britishrowing.org/wp-content/uploads/2018/05/Safety-Alert-take-care-setting-up-your-C2-rowing-machine-1.pdf](https://www.britishrowing.org/wp-content/uploads/2018/05/Safety-Alert-take-care-setting-up-your-C2-rowing-machine-1.pdf)
  * Prescribes **125–140** for Adult Heavyweight Men (with GB Rowing Team senior trials historically using ~135–138), **120–135** for Adult Lightweight Men, **120–130** for Adult Heavyweight Women, and **115–125** for Adult Lightweight Women.
* **Rowing Australia (*2000m and 5000m Ergometer Testing Protocol*, 2020):** [https://rowingaustralia.com.au/hubfs/2000m-and-5000m-Ergometer-Protocol-2020-Onwards.pdf](https://rowingaustralia.com.au/hubfs/2000m-and-5000m-Ergometer-Protocol-2020-Onwards.pdf)
  * Mandates fixed testing drag factors: **130** for Heavyweight Men, **125** for Lightweight & Junior Men, **110** for Heavyweight Women, and **100** for Lightweight & Junior Women.
* **Rowing Canada Aviron (*National Testing and Monitoring*, Nov 2020):** [https://rowingcanada.org/uploads/2020/12/Testing-and-Monitoring_Nov2020_FINAL.pdf](https://rowingcanada.org/uploads/2020/12/Testing-and-Monitoring_Nov2020_FINAL.pdf)
  * Mandates fixed testing drag factors: **130** for Open Men, **120** for Lightweight & Junior Men, **120** for Open Women, and **110** for Lightweight & Junior Women.

---

## 6. Empirical Regatta & Anthropometric Height Data Sources

The empirical pipeline in [`data/`](../data/) ([`fetch_crashb.py`](../data/fetch_crashb.py) and [`build_athlete_heights.py`](../data/build_athlete_heights.py)) downloads race results, 1 Hz PM5 telemetry, and verified athlete heights from the following public repositories and endpoints (caching raw downloads locally in git-ignored `data/raw/`):

### Time-Team Regatta Systems: C.R.A.S.H.-B. Sprints & WRIC Results / PM5 Telemetry
* **C.R.A.S.H.-B. Sprints Archives (2018–2020, 2022–2023, 2025–2026):**
  * [https://regatta.time-team.nl/crashb/2018](https://regatta.time-team.nl/crashb/2018)
  * [https://regatta.time-team.nl/crashb/2019](https://regatta.time-team.nl/crashb/2019)
  * [https://regatta.time-team.nl/crashb/2020](https://regatta.time-team.nl/crashb/2020)
  * [https://regatta.time-team.nl/crashb/2022](https://regatta.time-team.nl/crashb/2022)
  * [https://regatta.time-team.nl/crashb/2023](https://regatta.time-team.nl/crashb/2023)
  * [https://regatta.time-team.nl/crashb/2025](https://regatta.time-team.nl/crashb/2025)
  * [https://regatta.time-team.nl/crashb/2026](https://regatta.time-team.nl/crashb/2026)
* **World Rowing Indoor Championships (WRIC 2019, Long Beach, CA):**
  * [https://regatta.time-team.nl/wric/2019](https://regatta.time-team.nl/wric/2019)
* **Summary:** Official Time-Team regatta result tables (500m, 1,000m, 1,500m, and 2,000m splits plus average stroke rate `spm`) and 1 Hz PM5 ergometer race-chart telemetry logs harvested by [`data/fetch_crashb.py`](../data/fetch_crashb.py).

### Wikidata Query Service (SPARQL Endpoint): International & World Rowing Athlete Stature
* **SPARQL Endpoint:** [https://query.wikidata.org/sparql](https://query.wikidata.org/sparql)
* **Entities & Properties Queried:** Occupation rower ([`wd:Q13382576`](https://www.wikidata.org/wiki/Q13382576) via `wdt:P106`), World Rowing (FISA) athlete ID ([`wdt:P2091`](https://www.wikidata.org/wiki/Property:P2091)), physical stature/height ([`wdt:P2048`](https://www.wikidata.org/wiki/Property:P2048) normalized to centimeters), sex or gender ([`wdt:P21`](https://www.wikidata.org/wiki/Property:P21)), and multilingual labels/aliases (`rdfs:label`, `skos:altLabel`).
* **Summary:** Queried by [`data/build_athlete_heights.py`](../data/build_athlete_heights.py) to obtain verified heights for international, Olympic, and World Rowing championship competitors.

### Olympic Rowing Anthropometric Dataset (Griffin / Olympedia via R4DS TidyTuesday)
* **Direct CSV Endpoint:** [https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-07-27/olympics.csv](https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-07-27/olympics.csv)
* **Underlying Compilation:** Griffin, R. H. (2018), *"120 years of Olympic history: athletes and results"*, compiled from historical Olympic biographical records (`sports-reference.com` / Olympedia).
* **Summary:** Filtered to `sport == "Rowing"` records with verified `height` (cm) and `weight` (kg) by [`data/build_athlete_heights.py`](../data/build_athlete_heights.py).

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
* **Summary:** Parsed with `BeautifulSoup` and matched against regatta competitors via `rapidfuzz` token normalization (`rapidfuzz.fuzz.token_sort_ratio`, cutoff $\ge 90$) in [`data/build_athlete_heights.py`](../data/build_athlete_heights.py).
