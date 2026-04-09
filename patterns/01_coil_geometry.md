# Pattern 1: Special Coil Geometry

**Prevalence:** 61 of 768 patents (7.9%) — the most common recurring feature  
**Categories:** Primarily electromagnetic, some electrochemical

## What It Is

Across high-efficiency energy device patents, unconventional coil winding
geometries appear more than any other single feature. These aren't standard
solenoids — they are specific topologies chosen to exploit electromagnetic
properties that conventional windings don't access.

## Key Geometries Found in Patents

### 1. Bifilar Coil (Tesla, US512340)
Two parallel wires wound together in the same direction. Tesla's original
patent describes a coil where the two conductors are wound such that
adjacent turns belong to different windings, creating high mutual capacitance
between turns while maintaining high inductance.

**Why it matters:** The bifilar configuration creates a distributed LC circuit
within the coil itself. Each adjacent turn acts as a tiny capacitor plate.
This means the coil has a natural self-resonant frequency that is much more
pronounced than in conventional windings.

**Design principle:** Wind two insulated wires side-by-side on a former.
Connect the start of wire A to the end of wire B (series connection). The
resulting coil has very high distributed capacitance and a sharp resonant peak.

### 2. Toroidal Windings
Coils wound on a toroidal (donut-shaped) core. Appears in 6+ patents.
The toroid has a unique property: nearly all magnetic flux is confined within
the core, creating almost zero external field leakage.

**Why it matters:** The closed flux path means very high coupling efficiency
between windings. Some inventors (Rodin coil advocates) claim specific
winding patterns on toroids create unusual field effects.

**Design principle:** Wind on a toroidal ferrite core. For testing, use a
T200-2 (red) iron powder toroid, widely available. Wind primary and secondary
with the same number of turns for 1:1 coupling tests.

### 3. Pancake / Flat Spiral Coils
Flat coils wound in a spiral on a single plane, as used in Tesla's magnifying
transmitter designs. These appear in wireless power transfer patents and some
energy harvesting designs.

**Why it matters:** Flat spirals create a fundamentally different field
geometry than solenoids. The fields from each turn partially cancel in the
axial direction and reinforce in the radial plane, creating a wide, flat
field distribution.

### 4. Caduceus / Counter-Wound Coils
Two wires wound in opposite directions on the same core, creating opposing
magnetic fields. Less common in the patent database but referenced in
alternative energy literature.

**Why it matters:** The opposing fields theoretically cancel the magnetic
component while preserving an electric (scalar) component. This is the
basis for "scalar wave" claims.

## Co-Occurrence with Other Patterns

- **Coil geometry + permanent magnets** = 19 patents (strongest co-occurrence
  in the entire database)
- **Coil geometry + pulsed DC** = 5 patents
- **Coil geometry + specific frequencies** = 4 patents
- **Coil geometry + resonance** = 3 patents

The coil geometry + permanent magnet combination suggests that the interaction
between shaped magnetic fields (from magnets) and shaped electromagnetic
fields (from coils) is a key principle.

## Key Patents to Study

| Patent | Title | Inventor | Key Feature |
|---|---|---|---|
| US512340 | Coil for electro-magnets | Tesla | Bifilar winding, distributed capacitance |
| WO2023239247A1 | Device for generating energy by magnetic collapse | Illanes | Bifilar + permanent magnets + pulsed DC |
| SK412022U1 | High-frequency transformer | Marek | High stray inductance by design, resonant |
| GB2454171A | Reluctance machines with permanent magnets | Pollock | Integrated coil/magnet topology |
| JP7587520B2 | High energy capacitive conversion device | Elfman | Multifilar inductors for capacitor discharge |

## Actionable Design Principles

### Experiment 1: Bifilar Coil Resonance Characterization
**Goal:** Measure self-resonant frequency and Q factor of bifilar vs conventional coil

**Materials:**
- Magnet wire, 24-28 AWG, two spools (~$15)
- PVC pipe section, 2" diameter, 6" long (coil former)
- Function generator or NanoVNA ($30-50 for clone)
- Oscilloscope (or use NanoVNA S11 measurement)

**Procedure:**
1. Wind 100 turns of single wire on former (control coil)
2. Wind 100 turns bifilar (50 turns of doubled wire) on identical former
3. Measure impedance sweep 1 kHz to 30 MHz on both
4. Record: self-resonant frequency, impedance at resonance, Q factor
5. Compare the two — bifilar should show a sharper, lower-frequency resonance

### Experiment 2: Toroidal vs Solenoid Coupling Efficiency
**Goal:** Measure power transfer efficiency between primary and secondary

**Materials:**
- T200-2 iron powder toroid ($3)
- Magnet wire, 22 AWG
- Signal generator + oscilloscope
- 10Ω load resistor

**Procedure:**
1. Wind 30-turn primary + 30-turn secondary on toroid
2. Wind same turns on a straight ferrite rod (solenoid)
3. Drive primary at 1 kHz - 1 MHz, measure voltage across load on secondary
4. Calculate transfer efficiency at each frequency
5. Toroid should show near-unity coupling; solenoid will drop off with frequency

### Experiment 3: Flat Spiral Field Mapping
**Goal:** Map the field distribution of a flat spiral coil

**Materials:**
- Magnet wire wound in flat spiral on cardboard (30+ turns)
- Small pickup coil (10 turns on a pencil) or hall effect sensor
- Signal generator + oscilloscope

**Procedure:**
1. Drive spiral at several frequencies (1 kHz, 10 kHz, 100 kHz)
2. Map field strength at grid points above, below, and around coil
3. Note the field null points and maxima
4. Compare to theoretical predictions for flat spiral geometry

## Open Questions

1. Does the bifilar coil's self-resonant frequency shift under load, and does
   this shift correlate with any anomalous behavior?
2. What happens when you drive a bifilar coil at its self-resonant frequency
   vs. at other frequencies?
3. Is there a specific turn ratio or wire spacing that optimizes the
   distributed capacitance effect?
4. How do different core materials affect the bifilar coil's resonant behavior?
