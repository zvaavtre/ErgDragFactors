# Drag Factor (k) vs. Stroke Length (L) Models for a 2,000m Test

While there is no single universal formula that says *"if your stroke length is X meters, set your drag factor to Y,"* researchers (most notably [**Dr. Valery Kleshnev** at BioRow](03-references-and-literature.md#valery-kleshnev-biorow-handle-drag-factor) and [**Anu Dudhia** at Oxford](03-references-and-literature.md#anu-dudhia-oxford-the-physics-of-rowing)) have modeled the exact physical and biomechanical tradeoff between **Drag Factor** ($k$) and **Effective Drive Length** ($L_{\text{effective}}$) for a 2k test.

---

## 1. The Mechanical Model: "Catch Slip" vs. Drive Length

On a Concept2, your **reported Drive Length** ($L_{\text{effective}}$, logged via [ErgData](03-references-and-literature.md#concept2-ergdata-stroke-metrics-drive-length-drive-time-force)) is not how far your hands physically move ($L_{\text{total}}$); it is the distance the handle travels *while the chain is actually accelerating the flywheel* ([Dudhia, Oxford](03-references-and-literature.md#anu-dudhia-oxford-the-physics-of-rowing); [Kleshnev, 2016](03-references-and-literature.md#valery-kleshnev-the-biomechanics-of-rowing-2016--2020)):

$$L_{\text{effective}} = L_{\text{total}} - L_{\text{slip}}$$

At the start of the drive (the catch), the flywheel is already spinning at angular velocity $\omega_{\text{min}}$ left over from the previous stroke. Until your handle speed ($v_{\text{handle}}$) exceeds the linear speed of the chain sprocket ($r \cdot \omega_{\text{min}}$), the clutch freewheels and does zero work. The distance your hands travel before the clutch engages is **catch slip** ($L_{\text{slip}}$).

* **How Drag Factor ($k$) changes $\omega_{\text{min}}$:** During the recovery time ($t_{\text{rec}}$), the flywheel decelerates according to ([Dudhia, Oxford](03-references-and-literature.md#anu-dudhia-oxford-the-physics-of-rowing)):
  $$\omega_{\text{min}} = \frac{\omega_{\text{max}}}{1 + \frac{k}{I} \omega_{\text{max}} t_{\text{rec}}}$$
  (where $I \approx 0.1001\text{ kg}\cdot\text{m}^2$ is the Concept2 flywheel moment of inertia).
* **Low Drag Factor (k ≈ 90–110):** The flywheel decelerates very slowly ($\omega_{\text{min}}$ stays high). You must accelerate the handle much faster at the catch just to engage the clutch. This increases $L_{\text{slip}}$ and **shortens your effective stroke length** unless you have rapid front-end handle acceleration.
* **High Drag Factor (k ≈ 140–200):** The flywheel decelerates rapidly during recovery ($\omega_{\text{min}}$ drops low). The clutch engages earlier in the drive (smaller $L_{\text{slip}}$, lengthening the *engaged* stroke), **but** at the cost of much higher peak force and lower handle velocity ([Kleshnev & Dinares](03-references-and-literature.md#valery-kleshnev-and-carlos-dinares-on-water-vs-ergometer-drag-factors)).

---

## 2. The Biomechanical Model: Kleshnev’s Handle Drag Factor (HDF)

[Dr. Valery Kleshnev (RBN 2011/01)](03-references-and-literature.md#valery-kleshnev-biorow-handle-drag-factor) models the interaction of power ($P$), stroke rate ($R$), drive length ($L$), and resistance using the **Handle Drag Factor** ($\text{HDF}$), which relates average power to the cube of handle velocity ($v_{\text{drive}} = L / t_{\text{drive}}$):

$$P_{\text{drive}} = \text{HDF} \cdot \left(\frac{L}{t_{\text{drive}}}\right)^3 \implies W_{\text{stroke}} = \bar{F} \cdot L$$

For a target 2k split (which fixes your required average power $P$; see [Concept2 Power & Pace](03-references-and-literature.md#concept2-calculating-power-and-pace)), your work per stroke at stroke rate $R$ is $W_{\text{stroke}} = \frac{60 \cdot P}{R}$. Because $W_{\text{stroke}} = \bar{F} \cdot L$:

* **The Tall / Long-Stroke Athlete (L ≈ 1.45–1.60 m):** Because you have a long lever arm ($L$; see [Ingham et al., 2002](03-references-and-literature.md#ingham-et-al-2002-determinants-of-2000m-rowing-ergometer-performance)), you can generate large work per stroke ($W_{\text{stroke}}$) over a longer distance and time. However, if $k$ is too low, a tall rower has to move their larger body mass at an inefficiently high contraction velocity to beat $\omega_{\text{min}}$.
* **The Shorter Athlete (L ≈ 1.15–1.30 m):** With a shorter $L$, generating the same $W_{\text{stroke}}$ requires either a higher stroke rate ($R$) or higher average force ($\bar{F}$). If a shorter rower sets $k$ high to compensate for a short stroke, the peak force at the catch spikes into the anaerobic/alactic zone, causing rapid lactate buildup and lower-back failure by the 1,000m mark ([Kane et al., 2008](03-references-and-literature.md#kane-et-al-2008--2013-effects-of-drag-factor-and-stroke-resistance-on-rowing-physiology--economy); [Soper & Hume, 2004](03-references-and-literature.md#soper-and-hume-2004-towards-an-ideal-rowing-technique-for-performance)).

---

## 3. The 2k Fatigue Decay Curve (Stroke Length vs. Time)

Empirical 2k telemetry studies (tracking stroke-by-stroke PM5 data via [ErgData](03-references-and-literature.md#concept2-ergdata-stroke-metrics-drive-length-drive-time-force) and [BioRow](03-references-and-literature.md#valery-kleshnev-the-biomechanics-of-rowing-2016--2020); see also [Cerasola et al., 2017](03-references-and-literature.md#cerasola-et-al-2017-drag-factor-on-rowing-ergometer-during-2000-m-performance)) show a U-shaped failure model when pairing Drag Factor with Stroke Length over a 6-to-7-minute test:

1. **When Drag Factor is Too High (k > 140):**
   * *Meters 0–500:* Effective stroke length $L_{\text{effective}}$ looks great because $L_{\text{slip}}$ is near zero.
   * *Meters 1,000–2,000:* The high peak force required to overcome the dead flywheel fatigues fast-twitch (Type IIx) fibers in the quads and lumbar spine ([Kane et al., 2008](03-references-and-literature.md#kane-et-al-2008--2013-effects-of-drag-factor-and-stroke-resistance-on-rowing-physiology--economy); [Soper & Hume, 2004](03-references-and-literature.md#soper-and-hume-2004-towards-an-ideal-rowing-technique-for-performance)). To keep the stroke rate up when exhausted, the athlete subconsciously cuts the catch and layback short—**total stroke length** ($L_{\text{total}}$) **collapses by 8–15 cm** in the third 500m.
2. **When Drag Factor is Too Low (k < 105):**
   * *Meters 0–2,000:* Physical stroke length ($L_{\text{total}}$) stays long, and lower-back strain is low, but as neuromuscular coordination fades in the final 750m, hand speed at the catch slows down by milliseconds. Because the fan is spinning so fast, $L_{\text{slip}}$ balloons, and you end up "pulling air" for the first 15–20 cm of the drive.

---

## 4. Practical Lookup Model & Field Calibration Protocol

In applied sports science ([Cerasola et al., 2017](03-references-and-literature.md#cerasola-et-al-2017-drag-factor-on-rowing-ergometer-during-2000-m-performance); [Kleshnev & Dinares](03-references-and-literature.md#valery-kleshnev-and-carlos-dinares-on-water-vs-ergometer-drag-factors); [Ingham et al., 2002](03-references-and-literature.md#ingham-et-al-2002-determinants-of-2000m-rowing-ergometer-performance)), optimal 2k Drag Factor is modeled primarily by **body mass and lean leverage** rather than trying to force a higher damper for a shorter stroke:

| [Athlete Profile](00-tldr-height-and-style-guide.md#1-setup-by-rower-height) | Typical 2k Drive Length ($L$) | [Typical 2k Rate](02-fatigue-rate-and-catch-slip.md#3-the-optimal-2000m-rate-vs-slip-pacing-model) ($R$) | Optimal 2k Drag Factor ($k$) | [Approx. Damper](03-references-and-literature.md#concept2-damper-setting-101-and-explaining-drag-factor) (Clean Cage) |
| :--- | :--- | :--- | :--- | :--- |
| [**Heavyweight Men** (Tall / Long lever)](00-tldr-height-and-style-guide.md#tall-rowers) | 1.40 – 1.55 m | 32 – 36 spm | **125 – 135** *([up to 140 for power-dominant](00-tldr-height-and-style-guide.md#2-adjustments-by-physiology-aerobic-vs-force-dominant))* | ~4.5 – 5.5 |
| [**Lightweight Men / Heavyweight Women**](00-tldr-height-and-style-guide.md#medium-height-rowers) | 1.25 – 1.40 m | 33 – 37 spm | **115 – 125** *([±5–8 by physiology](00-tldr-height-and-style-guide.md#2-adjustments-by-physiology-aerobic-vs-force-dominant))* | ~3.5 – 4.5 |
| [**Lightweight Women / Shorter Rowers**](00-tldr-height-and-style-guide.md#shorter-rowers) | 1.10 – 1.25 m | 34 – 38+ spm | **105 – 115** | ~3.0 – 4.0 |

### How to Calibrate Your Personal Drag Factor vs. Stroke Length Sweet Spot
If you use the [**Concept2 ErgData** app](03-references-and-literature.md#concept2-ergdata-stroke-metrics-drive-length-drive-time-force) (which logs `Drive Length` in meters and `Drag Factor` for every stroke):
1. Do a **4 × 500m test-pace workout** at your target 2k split and stroke rate, testing four drag factors (e.g., **110, 120, 130, 140**).
2. Look at your **Drive Length** and **Peak/Avg Force ratio** in ErgData on the 3rd and 4th intervals:
   * If your `Drive Length` drops at **110**, you are losing front-end connection ($L_{\text{slip}}$ is eating your catch).
   * If your `Drive Length` or stroke rate drops at **135–140** while heart rate/perceived leg burn spikes, the resistance is stalling your handle velocity ($v_{\text{handle}}$) and forcing you to shorten up.
   * Your optimal 2k setting is the **lowest drag factor where your `Drive Length` at 2k pace/rate remains maxed out and stable**.
