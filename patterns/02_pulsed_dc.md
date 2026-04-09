# Pattern 2: Pulsed DC Waveforms

**Prevalence:** 47 of 768 patents (6.1%)  
**Categories:** Electromagnetic, plasma, electrochemical  
**Co-occurrence:** Strong overlap with plasma discharge (8 patents), coil geometry (5), specific frequencies (4)

## What It Is

A striking number of high-efficiency energy patents use pulsed direct current
rather than sinusoidal AC or steady DC. The pulse characteristics — rise time,
duty cycle, repetition rate, and shape — appear to be critical parameters,
not incidental ones. Many inventors specify sharp-edged pulses with very fast
rise times (nanosecond-scale).

## Why Pulsed DC Keeps Appearing

### 1. Sharp Edges Contain Broadband Frequency Content
A fast-rising pulse edge is equivalent to a superposition of many frequencies
(Fourier analysis). A 10ns rise time contains frequency components up to
~35 MHz. This means a single pulse can excite multiple resonant modes in a
system simultaneously.

### 2. Transient Response ≠ Steady-State Response
Most electrical engineering focuses on steady-state AC behavior. But during
transients (the moment of switching), different physics dominates:
- Displacement current (dE/dt) becomes significant
- Dielectric polarization effects appear
- Stored energy in parasitic capacitances becomes available
- Back-EMF spikes can exceed supply voltage by large multiples

### 3. Non-Linear Systems Behave Differently Under Impulse
In non-linear magnetic materials (ferrites, amorphous cores, even air-core
systems near saturation), pulsed excitation can access operating regions that
sinusoidal drive never reaches.

## Key Patents

| Patent | Inventor | Key Feature |
|---|---|---|
| US3890548 | Edwin Gray | Pulsed capacitor discharge motor — claims energy recovery from back-EMF |
| US4595975 | Edwin Gray | Capacitor discharge power supply for inductive loads |
| US5449989 | Correa & Correa | PAGD — specific pulse parameters in abnormal glow discharge |
| WO2023239247A1 | Jose Illanes | Energy generation by "magnetic collapse" using pulsed DC + bifilar coils |
| US12003202B2 | Tripathi | Pulsed electric machine control — modern take on pulsed motor drive |
| US4936961 | Stanley Meyer | Resonant pulsed electrolysis — pulse frequency tuned to cell resonance |

## The Gray Motor Principle (US3890548)

Edwin Gray's EMA (Electro-Magnetic Association) motor is perhaps the most
instructive example. The operating principle:

1. Charge a bank of capacitors from a battery
2. Discharge capacitors through electromagnets via a spark gap / switching tube
3. The sharp discharge pulse creates a strong magnetic impulse
4. As the magnetic field collapses, the back-EMF spike is captured by a
   second set of capacitors (the "recovery" bank)
5. The recovery bank is then used to recharge the battery

**The key claim:** The energy recovered from the collapsing field (step 4)
approaches or exceeds the energy initially stored in the discharge capacitors.

**Mainstream explanation:** In a conventional linear system, you can recover
at most 100% of stored energy (minus losses). Gray's claim implies either
a non-linear mechanism or an error in measurement.

**What to investigate:** The spark gap / switching element is critical. It
introduces a non-linear, plasma-based switching event. The combination of
pulsed DC + plasma switching + magnetic field collapse may create conditions
not captured by linear circuit analysis.

## The Meyer Principle (US4936961)

Stanley Meyer's water fuel cell uses pulsed DC at the resonant frequency of
the electrolytic cell:

1. The cell (water + electrodes) is treated as a capacitor (which it is —
   two plates separated by a dielectric)
2. A pulsed signal at the cell's resonant frequency is applied
3. Meyer claims that at resonance, voltage across the cell builds up
   (voltage multiplication), while current remains minimal
4. Water dissociation occurs via voltage (electric field) rather than
   current (electron flow)

**Mainstream explanation:** Faraday's law sets a minimum energy for electrolysis.
Meyer claimed to operate below this minimum by using voltage rather than current.

**What to investigate:** Whether resonant pulsing of an electrolytic cell
does in fact produce a measurably different gas volume per watt compared to
steady DC electrolysis.

## Actionable Design Principles

### Experiment 1: Pulsed vs Steady DC Electrolysis
**Goal:** Measure gas production efficiency under pulsed vs DC electrolysis

**Materials:**
- Two identical electrolysis cells (stainless steel plates, KOH electrolyte)
- DC power supply (0-30V, 0-5A)
- 555 timer circuit or signal generator for pulsing
- MOSFET for switching (IRFZ44N or similar)
- Gas collection tubes (inverted graduated cylinders over water)
- Multimeter for voltage/current measurement
- Watt-hour meter or current sense resistor + scope

**Procedure:**
1. Cell A: steady DC at, say, 12V
2. Cell B: pulsed DC at 12V peak, 50% duty cycle, sweeping frequency
   from 100 Hz to 100 kHz
3. Measure: input power (V × I, averaged), gas volume produced over 10 minutes
4. Calculate: mL of gas per watt-hour for each condition
5. Vary duty cycle (10%, 25%, 50%, 75%, 90%) at best frequency
6. Key measurement: does any pulsed condition produce more gas per watt-hour
   than steady DC?

### Experiment 2: Capacitor Discharge Through Inductor with Recovery
**Goal:** Measure energy recovery from magnetic field collapse

**Materials:**
- Capacitor bank: 4× 2200µF 50V electrolytic ($10)
- Inductor: large ferrite toroid wound with 50 turns of 18 AWG
- Fast diode for recovery (UF4007 or Schottky)
- Second capacitor bank (recovery bank), identical to first
- MOSFET + gate driver for switching
- Oscilloscope with current probe
- Arduino or 555 for timing control

**Procedure:**
1. Charge capacitor bank A to known voltage (e.g., 24V)
2. Calculate stored energy: E = ½CV² 
3. Fire MOSFET: discharge A through inductor
4. When current peaks (inductor fully energized), open MOSFET
5. Collapsing field drives current through diode into recovery bank B
6. Measure final voltage on bank B
7. Calculate recovered energy
8. Compare input vs recovered energy
9. Vary: pulse duration, inductor core material, switching speed

**What to look for:** The ratio of recovered/input energy as a function of
switching speed. Does faster switching (harder pulse edges) improve recovery?

### Experiment 3: Pulse Rise Time Sweep
**Goal:** Determine if pulse rise time affects system behavior

**Materials:**
- Fast pulse generator or MOSFET driver with adjustable rise time
- Inductor/coil as load
- Oscilloscope (100 MHz+ bandwidth)

**Procedure:**
1. Apply pulses to an inductor at fixed energy but varying rise time
2. Rise times to test: 1µs, 100ns, 10ns
3. Monitor: radiated EMI, back-EMF voltage, inductor current waveform
4. Look for qualitative changes in behavior at faster rise times

## Open Questions

1. Is there a critical rise time threshold below which qualitatively different
   behavior emerges?
2. Does the switching element matter? (MOSFET vs IGBT vs spark gap vs vacuum tube)
   — Several inventors specifically require spark gaps, which produce
   a different transient than semiconductor switches
3. What role does the displacement current (capacitive coupling) play during
   the pulse edge, especially in bifilar coils?
4. Can pulsed electrolysis efficiency gains be explained by localized heating,
   bubble dynamics, or electrode surface effects?
