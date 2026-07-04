# Priority Experiments — 2026 Re-Evaluation

_Supersedes the ranking in [`10_synthesis.md`](10_synthesis.md). Derived from the
enriched corpus (full claims, CPC/IPC, LLM-extracted mechanism summaries) and the
model-read synthesis in [`11_semantic_synthesis.md`](11_semantic_synthesis.md) —
not the original keyword-frequency pass in `analyze_patterns.py`._

## Why the original ranking was re-evaluated

The first 29 experiments (patterns 01–09) and the `10_synthesis.md` flagship were
built on `analyze_patterns.py` — regex keyword-counting over one-sentence
abstracts. Once the corpus was enriched with full claims and read mechanistically
(766 of 768 patents fingerprinted), three things became clear:

1. **The "meta-pattern" was largely a keyword artifact.** The synthesis claimed the
   winning recipe is *non-linear element + resonance + pulsed excitation*. In the
   read data, only **13 of 766 patents** exhibit that full triple, and only **6**
   of those assert any anomalous effect. 72% of the corpus has *no* non-linear
   element; 83% has *no* resonance. The regex counted the three terms appearing
   *somewhere* across the corpus and inferred they combine; mechanistically they
   rarely do.
2. **The `category` tags are unreliable.** The "lenr" bucket contains xerographic
   toner chemistry, a DNA vaccine, and lithium batteries; "solid-state" contains
   OLED stacks and drug-delivery nanoparticles. A large minority of the 768 aren't
   energy-generation devices at all. Rank by **mechanism**, not category.
3. **Most eye-catching over-unity claims are singletons (noise), not patterns.**
   The signal worth chasing is **independent-inventor convergence** — the same
   mechanism template arrived at by unrelated filers across decades and countries.

Net: the experiments aren't *wrong physics*, but their **prioritization was
inverted**. ~101 patents assert a genuinely anomalous effect, and they do not
cluster where the flagship pointed.

## What changed vs. the original 29

| Original pattern | Anomalous-claim support (read data) | Disposition |
|---|---|---|
| P6 Water-splitting (4 exp) | 28 (anomalous gas yield; W2 convergence) | **KEEP** — best-supported |
| P7 LENR (3 exp) | 21 (17 excess-heat; W5 convergence) | **KEEP + elevate** (add calorimetry) |
| P4 Plasma (3 exp) | 13 (PAGD; W4) | **KEEP** |
| P8 Feedback / self-oscillation (3 exp) | self-sustaining + W3 convergence | **KEEP** — now the #1 priority |
| P2 Pulsed DC (3 exp) | pulsed = #2 anomalous input | **KEEP** |
| P1 Coil geometry (3 exp) | ~0 anomalous-claim patents | **DEMOTE** to Level-1 characterization |
| P3 Resonance-as-pillar (3 exp) | resonance in only 17% of corpus | **REFINE** — fold into P6 (Meyer subset) |
| P5 Permanent magnets (3 exp) | magnetic-static = 5 anomalous | **REFINE** — keep flux-switching, drop Halbach mapping |
| P9 Special materials (4 exp) | component-level, mostly conventional | **REFINE** — Level-1 supporting, not anomaly tests |
| `10_synthesis` flagship (EM triple) | 6 patents have the full triple | **DEMOTE from flagship** → teaching experiment only |
| — Casimir / ambient-EM DC (W1) | 7+ patents, independent convergence | **NEW** — no prior experiment existed |

The original 29 remain valid as **Level-1 / component-characterization** work. The
experiments below are the new **priority set**, ranked by *independent-inventor
convergence × how cheaply the core claim can be falsified*.

## The revised priority experiments

### Experiment 1: Back-EMF / Magnetic-Collapse Recovery — Net-Gain Falsification
**Goal:** Build the (real) back-EMF/inductive-collapse recovery hardware and settle whether the *net-gain* claim survives a closed loop, not just whether recovery works.
The recovery motif recurs across honest engineering (US11863096B2, US9716424B2, JP7587520B2) and over-unity claims (US20020097013A1, WO2023239247A1, US10008916B2) — the hardware is worth building; the over-unity assertion is the thing to kill.
**Cheapest falsifying test:** Battery-to-battery closed loop with coulomb counting — two matched cells, integrate amp-hours in vs. out over N cycles at matched chemistry/temperature. If net charge transferred ≤ input within meter error, the over-unity claim (not the recovery function) is falsified.
**Est. cost:** ~$50 (shunts + logging DMM). **Rank 1 — buildable and falsifiable in one measurement.**

### Experiment 2: Resonant-Pulse Water Electrolyser — Anomalous HHO Yield Falsification
**Goal:** Test the recurring "tune an electrical/acoustic resonance to break O–H below the Faraday minimum" claim (W2 — Meyer US4936961, plus RU2456377C1, RU2515884C1, WO2017004732A1, US20210156037A1 across the US, Russia, Chile, Japan over ~30 years with no citation lineage).
**Cheapest falsifying test:** Eudiometer + inline wattmeter — compute gas volume per coulomb vs. Faraday's law (~7 mL H₂ per amp-minute at STP). Sweep the resonance while watching the ratio; any claim beyond ~100% Faradaic efficiency is falsified directly.
**Est. cost:** ~$30 (graduated gas column, hall-effect current sensor). **Rank 2.**

### Experiment 3: Casimir / Plasmon-Cavity DC Harvester
**Goal:** Probe the most internally-consistent anomalous cluster (W1) — an asymmetric Casimir/plasmon cavity feeding a diode-like transport element as a claimed DC source, arrived at independently by Moddel (US11563388B2, US11463026B2, US11837971B2, US11258379B2), Bressi (US20190207537A1), and Villalobos (US20180059704A1). This mechanism has **no experiment in the original 29**.
**Cheapest falsifying test:** Fabricate the diode-adjacent nano-gap device (cheapest honest attempt: an existing tunnel/Schottky diode against a metallized dielectric), place it in a grounded Faraday enclosure at thermal equilibrium — no gradient, no RF — and log open-circuit voltage / short-circuit current with a nanovoltmeter over hours. Sustained DC into a load under those conditions is the extraordinary result; its absence falsifies.
**Est. cost:** ~$200 + lab access (fabrication is the cost driver; the test is clean). **Rank 3.**

### Experiment 4: Metal-Hydride LENR Excess-Heat Cell with Stimulation
**Goal:** Test the W5 convergence — H/D-loaded Ni or Pd lattice "rung" by a stimulation modality (current spikes, PWM magnetic pulses, ultrasound, THz-tuned plasma), where the substrate is constant and only the stimulation varies: Godes (US20220208399A1), Winzeler (US20250022619A1), Cook/acoustic (US20110044419A1), Letts/THz (US11008666B2).
**Cheapest falsifying test:** Isoperibolic (or simple flow) calorimetry with a blank control — an identical cell loaded with a non-hydriding metal under the same drive. Output thermal power minus input electrical power must exceed the blank by more than calorimeter uncertainty to survive. One afternoon with a Dewar, two thermocouples, and a resistive-heater calibration.
**Est. cost:** ~$150. **Rank 4 — real independent convergence; cheap-ish, decisive calorimetry.**

### Experiment 5: Ambient-RF / Atmospheric "Self-Sustaining" Collector — Shielded A/B
**Goal:** Separate legitimate bounded RF harvesting from the "self-sustaining source" claim in the Tesla-lineage ambient collectors (US685957, US787412, WO2005055409A2), contrasted with honest rectennas (CN110112546A, US11936413B1).
**Cheapest falsifying test:** Shielded-vs-unshielded A/B — measure delivered power, then enclose the collector in a Faraday cage. Honest RF harvesting drops to ~zero (it was bounded ambient flux); a claim of continued self-sustaining output is falsified by the cage.
**Est. cost:** ~free with a screen room or metal box. **Rank 5.**

### Experiment 6: Rotating-Field Collisional-Plasma Reactor
**Goal:** Diagnostic-only check of the W4 rotating-field (E×B) "low-energy fusion" claim (Wong US10269458B2, WO2019143396A2; adjacent Egely US20140126679A1).
**Cheapest falsifying test:** Neutron / activation counting at the claimed operating point (moderated ³He or bubble dosimeter) plus calorimetric input/output. Cheap on the *diagnostic* side (rented dosimeter); the reactor build itself is expensive and hazardous.
**Est. cost:** diagnostic ~rental; build high. **Rank 6 — last on prototyping practicality; include only for completeness.**

---

**Bottom line:** the corpus's real mineable value is the *conventional* convergence
(back-EMF/charge recovery, Halbach flux concentration, fractional-order WPT,
thermoelectric bottoming). The anomalous whitespace worth a cheap look is **W1
(Casimir DC)** and **W3-honest (recovery loops)** — recurrently and independently
claimed, and settleable with a single meter. Everything flagged `over_unity` as a
singleton, and every title-only/low-confidence fingerprint, is absence of
evidence, not evidence.
