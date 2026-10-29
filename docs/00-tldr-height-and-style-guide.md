# TL;DR: 2k Stroke Length, Rate & Drag Factor Guide (By Height & Physiology)

Direct, mechanical guidelines for setting your Concept2 PM5 **Drag Factor** (`More Options > Display Drag Factor`; see [Concept2 Drag Factor Guide](03-references-and-literature.md#concept2-damper-setting-101-and-explaining-drag-factor)) and managing **Stroke Length** and **Stroke Rate** during a 2,000m test.

---

## 1. Setup by Rower Height

Your height and limb lengths determine the distance the handle travels (`Drive Length` in [ErgData](03-references-and-literature.md#concept2-ergdata-stroke-metrics-drive-length-drive-time-force)) and the body mass you have to accelerate and decelerate along the monorail every stroke ([Ingham et al., 2002](03-references-and-literature.md#ingham-et-al-2002-determinants-of-2000m-rowing-ergometer-performance); [Kleshnev & Dinares](03-references-and-literature.md#valery-kleshnev-and-carlos-dinares-on-water-vs-ergometer-drag-factors)).

<a id="tall-rowers"></a>
### Tall Rowers (6'2"+ / 188 cm+)
* **Typical Drive Length:** **1.45 – 1.60 m** ([Stroke Length Model](01-drag-factor-vs-stroke-length.md#2-the-biomechanical-model-kleshnevs-handle-drag-factor-hdf))
* **Target Drag Factor:** **125 – 138** *(Damper ~4.5 – 5.5)* ([Mikulić et al., 2017](03-references-and-literature.md#mikulic-et-al-2017-optimal-drag-factor-for-2000m-rowing-ergometer-performance))
* **Base 2k Rate:** **30 – 34 spm** ([Rate & Pacing Model](02-fatigue-rate-and-catch-slip.md#3-the-optimal-2000m-rate-vs-slip-pacing-model))
* **Mechanical Advantage:** High work per stroke ($W = \bar{F} \cdot L$; see [Kleshnev HDF](03-references-and-literature.md#valery-kleshnev-biorow-handle-drag-factor)). Because the handle travels over a longer path, you can produce high wattage without needing an extreme stroke rate.
* **Common Failure Mode:** Setting the drag factor too low (< 115) or rating too high too early. Moving a larger body mass back and forth on the slide 36+ times per minute carries a high internal metabolic cost before any force is even applied to the handle.
* **Adjustment Under Fatigue (1,000m–1,500m):** Keep the recovery controlled rather than rushing the slide to force the rate up. Allowing the flywheel an extra tenth of a second to decelerate on the recovery reduces catch slip ([Dudhia](03-references-and-literature.md#anu-dudhia-oxford-the-physics-of-rowing)) and lets you apply full force through the legs and trunk swing.

<a id="medium-height-rowers"></a>
### Medium-Height Rowers (5'9"–6'1" / 175–185 cm)
* **Typical Drive Length:** **1.30 – 1.45 m** ([Stroke Length Model](01-drag-factor-vs-stroke-length.md#2-the-biomechanical-model-kleshnevs-handle-drag-factor-hdf))
* **Target Drag Factor:** **115 – 128** *(Damper ~3.5 – 4.5)* ([Mikulić et al., 2017](03-references-and-literature.md#mikulic-et-al-2017-optimal-drag-factor-for-2000m-rowing-ergometer-performance))
* **Base 2k Rate:** **33 – 36 spm** ([Rate & Pacing Model](02-fatigue-rate-and-catch-slip.md#3-the-optimal-2000m-rate-vs-slip-pacing-model))
* **Mechanical Advantage:** Balanced trade-off between work per stroke and slide mass. You can shift between higher force per stroke and higher turnover without the severe slide-inertia penalty of taller rowers.
* **Common Failure Mode:** Reaching beyond your active hip and ankle mobility (forcing extra handle travel by rounding the lumbar spine or dropping the shoulders after the pelvis has stopped rotating; see [Soper & Hume, 2004](03-references-and-literature.md#soper-and-hume-2004-towards-an-ideal-rowing-technique-for-performance)). Deep compression at the catch is effective on a stationary erg if your ankle dorsiflexion and hip flexion support it, but exceeding your active range of motion eliminates your stretch reflex and delays handle acceleration ($a_{\text{catch}}$).
* **Adjustment Under Fatigue (1,000m–1,500m):** Move the hands and torso away cleanly at the finish so you don't have to rush the final portion of the slide into the catch. Compress only as far as your active mobility allows you to reverse direction immediately.

<a id="shorter-rowers"></a>
### Shorter Rowers (Under 5'9" / under 175 cm)
* **Typical Drive Length:** **1.10 – 1.28 m** ([Stroke Length Model](01-drag-factor-vs-stroke-length.md#2-the-biomechanical-model-kleshnevs-handle-drag-factor-hdf))
* **Target Drag Factor:** **105 – 118** *(Damper ~3.0 – 4.0)* ([Kleshnev & Dinares](03-references-and-literature.md#valery-kleshnev-and-carlos-dinares-on-water-vs-ergometer-drag-factors))
* **Base 2k Rate:** **35 – 40 spm** ([Rate & Pacing Model](02-fatigue-rate-and-catch-slip.md#3-the-optimal-2000m-rate-vs-slip-pacing-model))
* **Mechanical Advantage:** Lower slide inertia and faster turnaround times. You can sustain higher stroke rates at a much lower internal energy cost than taller rowers.
* **Common Failure Mode:** **Setting the damper high (6–10) to compensate for a shorter stroke.** Because your drive length ($L$) is shorter, producing the same work per stroke at a high drag factor requires disproportionately high peak force at the catch, leading to rapid localized muscular fatigue in the quads and lower back before the 1,000m mark ([Kane et al., 2008](03-references-and-literature.md#kane-et-al-2008-effects-of-drag-factor-on-physiological-aspects-of-rowing); [Soper & Hume, 2004](03-references-and-literature.md#soper-and-hume-2004-towards-an-ideal-rowing-technique-for-performance)).
* **Adjustment Under Fatigue (1,000m–1,500m):** Rely on cadence rather than heavy resistance. Keep the drag factor lower (105–115), maintain posture at the catch, and keep the handle moving continuously through the transitions at both ends of the stroke.

---

## 2. Adjustments by Physiology (Aerobic vs. Force-Dominant)

Rowers of the same height often differ in muscle fiber composition and aerobic capacity ([Ingham et al., 2002](03-references-and-literature.md#ingham-et-al-2002-determinants-of-2000m-rowing-ergometer-performance); [Kane et al., 2008](03-references-and-literature.md#kane-et-al-2008-effects-of-drag-factor-on-physiological-aspects-of-rowing)):

| Parameter | **Aerobic / Turnover-Dominant** (High VO₂max relative to peak force) | **Force / Strength-Dominant** (High peak force and anaerobic capacity) |
| :--- | :--- | :--- |
| **Drag Factor Adjustment** | Subtract **5–8 points** from your height bracket (e.g., 112–120). | Add **5–8 points** to your height bracket (e.g., 128–138). |
| **Flywheel Mechanics** | Keeps minimum flywheel speed ($\omega_{\text{min}}$) higher via shorter recovery times so peak force per stroke stays lower. | Allows the flywheel to decelerate slightly more on the recovery, trading higher peak force for a lower stroke rate. |
| **Primary Technical Focus** | **Rapid turnaround at the catch** — handle acceleration ($a_{\text{catch}}$) must be fast so the clutch engages immediately against a fast-spinning flywheel. | **Drive-to-recovery ratio** — accelerate the handle quickly on the drive, then take a controlled recovery so working muscles can perfuse between strokes. |
| **3rd 500m Adjustment** | Hold stroke rate steady (35+ spm); if catch engagement slows down, reduce catch compression by 1–2 cm to stay inside your fastest rebound range. | Hold rate steady (31–33 spm) and maintain full drive length through complete leg extension and trunk swing. |

---

## 3. Core Principles for Managing Rate and Catch Slip

1. **Do Not Rush the Recovery When Fatigued (1,000m–1,600m):**
   As fatigue reduces your rate of force development at the catch ($a_{\text{catch}}$), rushing the recovery to increase stroke rate shortens the time the flywheel has to decelerate. Your slower legs then meet a faster-spinning flywheel ($\omega_{\text{min}}$), which increases **catch slip** ($L_{\text{slip}} \propto \omega_{\text{min}}^2 / a_{\text{catch}}$)—meaning the handle moves 15–20 cm before the clutch engages. Keep the recovery controlled so the flywheel decelerates enough for your legs to engage it immediately.
2. **Raising the Rate in the Final Sprint (Last 350m):**
   When peak force declines at the end of the piece, raising the stroke rate (+3 to 6 spm) keeps the flywheel spinning fast so less torque is required per stroke. Because $\omega_{\text{min}}$ is higher at 38+ spm, avoid pausing at full compression—use the stretch reflex to reverse direction immediately, or reduce compression by 1–2 cm if fatigue is slowing down your turnaround at the front end.
3. **Active Compression vs. Unloaded Reach:**
   Deep compression on an ergometer increases effective work per stroke **if** your hip and ankle mobility allow you to maintain pelvic position and rebound quickly. Reaching beyond your active flexibility by flexing the lumbar spine ([Soper & Hume, 2004](03-references-and-literature.md#soper-and-hume-2004-towards-an-ideal-rowing-technique-for-performance)) adds unloaded handle travel ($L_{\text{slip}}$; [Kleshnev, 2016](03-references-and-literature.md#valery-kleshnev-the-biomechanics-of-rowing-2016)) where force is too low to accelerate the flywheel.
4. **Monitoring `Drive Length` in ErgData:**
   If your logged `Drive Length` ([Concept2 ErgData](03-references-and-literature.md#concept2-ergdata-stroke-metrics-drive-length-drive-time-force)) drops by more than **5 cm** between the first 500m and third 500m, either your drag factor is too high (causing premature muscular fatigue and shortened strokes) or you are rushing the recovery and losing engagement at the catch.
