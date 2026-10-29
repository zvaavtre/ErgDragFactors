# Drag Factor ($k$) vs. Stroke Length ($L$) Models for a 2,000m Test

While there is no single universal formula that says *"if your stroke length is $X$ meters, set your drag factor to $Y$,"* researchers (most notably **Dr. Valery Kleshnev** at BioRow and **Anu Dudhia** at Oxford) have modeled the exact physical and biomechanical tradeoff between **Drag Factor ($k$)** and **Effective Drive Length ($L_{\text{effective}}$)** for a 2k test.

---

## 1. The Mechanical Model: "Catch Slip" vs. Drive Length

On a Concept2, your **reported Drive Length ($L_{\text{effective}}$)** is not how far your hands physically move ($L_{\text{total}}$); it is the distance the handle travels *while the chain is actually accelerating the flywheel*:

$$L_{\text{effective}} = L_{\text{total}} - L_{\text{slip}}$$

At the start of the drive (the catch), the flywheel is already spinning at angular velocity $\omega_{\text{min}}$ left over from the previous stroke. Until your handle speed ($v_{\text{handle}}$) exceeds the linear speed of the chain sprocket ($r \cdot \omega_{\text{min}}$), the clutch freewheels and does zero work. The distance your hands travel before the clutch engages is **catch slip ($L_{\text{slip}}$)**.

* **How Drag Factor ($k$) changes $\omega_{\text{min}}$:** During the recovery time ($t_{\text{rec}}$), the flywheel decelerates according to:
  $$\omega_{\text{min}} = \frac{\omega_{\text{max}}}{1 + \frac{k}{I} \omega_{\text{max}} t_{\text{rec}}}$$
  *(where $I \approx 0.1001\text{ kg}\cdot\text{m}^2$ is the Concept2 flywheel moment of inertia).*
* **Low Drag Factor ($k \approx 90\text{–}110$):** The flywheel decelerates very slowly ($\omega_{\text{min}}$ stays high). You must accelerate the handle much faster at the catch just to engage the clutch. This increases $L_{\text{slip}}$ and **shortens your effective stroke length** unless you have rapid front-end handle acceleration.
* **High Drag Factor ($k \approx 140\text{–}200$):** The flywheel decelerates rapidly during recovery ($\omega_{\text{min}}$ drops low). The clutch engages earlier in the drive (smaller $L_{\text{slip}}$, lengthening the *engaged* stroke), **but** at the cost of much higher peak force and lower handle velocity.

---

## 2. The Biomechanical Model: Kleshnev’s Handle Drag Factor (HDF)

Dr. Valery Kleshnev models the interaction of power ($P$), stroke rate ($R$), drive length ($L$), and resistance using the **Handle Drag Factor ($\text{HDF}$)**, which relates average power to the cube of handle velocity ($v_{\text{drive}} = L / t_{\text{drive}}$):

$$P_{\text{drive}} = \text{HDF} \cdot \left(\frac{L}{t_{\text{drive}}}\right)^3 \implies W_{\text{stroke}} = \bar{F} \cdot L$$

For a target 2k split (which fixes your required average power $P$), your work per stroke at stroke rate $R$ is $W_{\text{stroke}} = \frac{60 \cdot P}{R}$. Because $W_{\text{stroke}} = \bar{F} \cdot L$:

* **The Tall / Long-Stroke Athlete ($L \approx 1.45\text{–}1.60\text{ m}$):** Because you have a long lever arm ($L$), you can generate large work per stroke ($W_{\text{stroke}}$) over a longer distance and time. However, if $k$ is too low, a tall rower has to move their larger body mass at an inefficiently high contraction velocity to beat $\omega_{\text{min}}$.
* **The Shorter Athlete ($L \approx 1.15\text{–}1.30\text{ m}$):** With a shorter $L$, generating the same $W_{\text{stroke}}$ requires either a higher stroke rate ($R$) or higher average force ($\bar{F}$). If a shorter rower sets $k$ high to compensate for a short stroke, the peak force at the catch spikes into the anaerobic/alactic zone, causing rapid lactate buildup and lower-back failure by the 1,000m mark.

---

## 3. The 2k Fatigue Decay Curve ($L$ vs. Time)

Empirical 2k telemetry studies (tracking stroke-by-stroke PM5 data via ErgData/RP3/BioRow) show a U-shaped failure model when pairing Drag Factor with Stroke Length over a 6-to-7-minute test:

1. **When Drag Factor is Too High ($k > 140$):**
   * *Meters 0–500:* Effective stroke length $L_{\text{effective}}$ looks great because $L_{\text{slip}}$ is near zero.
   * *Meters 1,000–2,000:* The high peak force required to overcome the dead flywheel fatigues fast-twitch (Type IIx) fibers in the quads and lumbar spine. To keep the stroke rate up when exhausted, the athlete subconsciously cuts the catch and layback short—**total stroke length ($L_{\text{total}}$) collapses by 8–15 cm** in the third 500m.
2. **When Drag Factor is Too Low ($k < 105$):**
   * *Meters 0–2,000:* Physical stroke length ($L_{\text{total}}$) stays long, and lower-back strain is low, but as neuromuscular coordination fades in the final 750m, hand speed at the catch slows down by milliseconds. Because the fan is spinning so fast, $L_{\text{slip}}$ balloons, and you end up "pulling air" for the first 15–20 cm of the drive.

---

## 4. Practical Lookup Model & Field Calibration Protocol

In applied sports science (used by national teams and indoor Crash-B competitors), optimal 2k Drag Factor is modeled primarily by **body mass and lean leverage** rather than trying to force a higher damper for a shorter stroke:

| Athlete Profile | Typical 2k Drive Length ($L$) | Typical 2k Rate ($R$) | Optimal 2k Drag Factor ($k$) | Approx. Damper (Clean Cage) |
| :--- | :--- | :--- | :--- | :--- |
| **Heavyweight Men** (Tall / Long lever) | $1.40 - 1.55\text{ m}$ | $32 - 36\text{ spm}$ | **125 – 135** *(up to 140 for power-dominant)* | ~4.5 – 5.5 |
| **Lightweight Men / Heavyweight Women** | $1.25 - 1.40\text{ m}$ | $33 - 37\text{ spm}$ | **115 – 125** | ~3.5 – 4.5 |
| **Lightweight Women / Shorter Rowers** | $1.10 - 1.25\text{ m}$ | $34 - 38+\text{ spm}$ | **105 – 115** | ~3.0 – 4.0 |

### How to Calibrate Your Personal $k$ vs. $L$ Sweet Spot
If you use the **Concept2 ErgData** app (which logs `Drive Length` in meters and `Drag Factor` for every stroke):
1. Do a **4 × 500m test-pace workout** at your target 2k split and stroke rate, testing four drag factors (e.g., **110, 120, 130, 140**).
2. Look at your **Drive Length** and **Peak/Avg Force ratio** in ErgData on the 3rd and 4th intervals:
   * If your `Drive Length` drops at **110**, you are losing front-end connection ($L_{\text{slip}}$ is eating your catch).
   * If your `Drive Length` or stroke rate drops at **135–140** while heart rate/perceived leg burn spikes, the resistance is stalling your handle velocity ($v_{\text{handle}}$) and forcing you to shorten up.
   * Your optimal 2k setting is the **lowest drag factor where your `Drive Length` at 2k pace/rate remains maxed out and stable**.
