# Pattern 6: Anomalous Water Splitting

**Prevalence:** 34 of 768 patents (4.4%)  
**Categories:** Electrochemical, electromagnetic  
**Co-occurrence:** Resonance (3), plasma discharge (3)

## What It Is

Water electrolysis — splitting H₂O into H₂ and O₂ — is governed by
Faraday's laws of electrolysis and thermodynamic limits. The theoretical
minimum energy is 237 kJ/mol (for liquid water → gaseous products at STP),
corresponding to 1.23V per cell. Practical electrolysis typically requires
1.8-2.0V due to overpotentials and resistance.

Multiple patents claim to achieve electrolysis at significantly reduced
energy input, typically through one or more of:
- Resonant pulsed driving (Meyer)
- Cavitation-assisted dissociation
- Plasma electrolysis
- Novel electrode geometries and materials

## The Faraday Minimum Question

Faraday's first law: mass of substance produced ∝ charge passed (current × time).

This sets a hard floor: 26.8 Ah per mole of H₂ (2 grams). You cannot
produce hydrogen with less charge than this.

**But:** Faraday's law governs *charge* (current × time), not *energy*
(voltage × current × time). If you can reduce the voltage while maintaining
the required charge transfer, you reduce total energy.

The thermodynamic minimum voltage is 1.23V. Below this, electrolysis
shouldn't occur spontaneously. But:
- At elevated temperature, the minimum voltage decreases
- At the electrode surface, local conditions may differ from bulk
- Catalysts can lower overpotentials
- Non-equilibrium conditions (pulsing, cavitation) may alter the energetics

## Key Patents & Approaches

### 1. Stanley Meyer — Resonant Electrolysis (US4936961)
Claims water splitting via high-voltage, low-current resonant pulsing.
The cell is treated as a capacitor in an LC tank circuit. At resonance,
voltage across the cell builds to high levels while current remains small.
Meyer claimed the electric field (not current) drives dissociation.

**Status:** Meyer died in 1998. Several replication attempts exist with
mixed results. The patent is detailed enough to attempt replication.

### 2. McKane Lee — Quantum Kinetic Fusor (US20210156037A1)
A more recent patent describing "electrolysis using voltage in a purely
physical process, without resorting to passing current through an
electrolyte." Explicitly references resonant driving.

### 3. Plasma Electrolysis
When electrolysis voltage exceeds ~100V, a plasma sheath forms around
the cathode. In this regime:
- Local temperatures reach 3000-10000K
- Water molecules are dissociated thermally AND electrically
- Gas production rates can exceed Faraday predictions
  (because thermal dissociation adds to electrochemical dissociation)
- Transmutation of elements has been reported (controversial)

### 4. Cavitation-Assisted Splitting
Ultrasonic cavitation creates microscopic bubbles that collapse violently,
producing extreme local temperatures and pressures. Some patents combine
cavitation with electrolysis, claiming enhanced gas production.

### 5. Roy McAlister (7+ patents)
The most prolific inventor in our electrochemical dataset. His patents cover
nucleation control, multi-source hydrogen production, and novel electrode
designs. Key patents: US8172990B2, US20130240369A1, EP2398937B1.

McAlister's approach: control the nucleation of gas bubbles at electrode
surfaces to reduce the energy wasted in bubble formation and detachment.

## The Measurement Problem

Claims of anomalous water splitting efficiency are controversial. Common
measurement pitfalls:

1. **Not measuring true input power.** Pulsed systems have complex
   V×I waveforms. Average power ≠ peak power × duty cycle unless the
   waveform is purely resistive. Reactive power must be accounted for.
2. **Gas volume measurement errors.** Temperature, pressure, and water
   vapor content all affect measured gas volume.
3. **Recombination.** H₂ and O₂ can recombine at the electrode surface
   or in the gas space, reducing apparent yield.
4. **Mixed gases.** HHO (Brown's gas) is a H₂/O₂ mix, sometimes with
   water vapor. Not all measured gas volume is combustible.

## Actionable Design Principles

### Experiment 1: Baseline Electrolysis Efficiency
**Goal:** Establish a rigorous baseline for electrolysis efficiency before
testing any novel approaches

**Materials:**
- Electrolysis cell: 316 stainless steel plates, 50×50mm, 2mm gap
- Electrolyte: distilled water + 5% KOH by weight
- DC power supply: 0-30V, 0-5A
- Gas collection: inverted graduated cylinder over water (displacement method)
- Measurements: true RMS multimeter, ideally oscilloscope + current probe
- Thermometer for gas temperature
- Barometer or weather app for atmospheric pressure
- Timer

**Procedure:**
1. Run steady DC electrolysis at 2.0V, 3.0V, 5.0V, 10.0V per cell
2. At each voltage, measure:
   - Voltage across cell
   - Current through cell
   - Gas volume collected per minute
   - Gas temperature
   - Ambient pressure
3. Correct gas volume to STP: V_stp = V_measured × (P/P₀) × (T₀/T)
4. Calculate moles of gas: n = V_stp / 22,400 mL/mol
5. Calculate Faraday efficiency: η = n_actual / n_theoretical
   where n_theoretical = (I × t) / (2 × 96485)
6. Calculate energy efficiency: η_e = (n × 237000 J/mol) / (V × I × t)
7. This is your baseline. All novel approaches must beat this.

### Experiment 2: Pulsed vs DC at Matched Power
**Goal:** Test whether pulsing improves efficiency

**Materials:**
- Same cell as Experiment 1
- Signal generator + MOSFET driver for pulsing
- TRUE RMS power measurement (this is critical)

**Procedure:**
1. Run DC at known power level, measure gas production (from Exp 1)
2. Switch to pulsed at same AVERAGE power (adjust duty cycle/amplitude)
3. Test frequencies: 100 Hz, 1 kHz, 10 kHz, 100 kHz
4. Test duty cycles: 10%, 25%, 50%, 75%
5. At each condition, collect gas for 10 minutes and measure volume

**Critical measurement note:** Use oscilloscope to multiply V(t) × I(t)
instantaneously and integrate. Do NOT use V_avg × I_avg — this will give
incorrect power for pulsed waveforms.

### Experiment 3: Resonant Cell Drive
**Goal:** Test the Meyer resonant electrolysis concept

**Materials:**
- Tubular cell: inner and outer stainless steel tubes (concentric)
  — Meyer's original patent specifies this geometry
- Variable inductor or set of inductors (10µH to 10mH)
- NanoVNA for impedance measurement
- Signal generator + amplifier
- Gas collection apparatus

**Procedure:**
1. Build concentric tube cell per Meyer patent specifications
2. Measure cell impedance vs frequency (find capacitance)
3. Add series inductor to form resonant circuit
4. Calculate expected resonant frequency: f = 1/(2π√(LC))
5. Verify with NanoVNA — impedance should dip at resonant frequency
6. Drive at resonant frequency with gradually increasing voltage
7. Measure gas production and input power
8. Compare to DC baseline at same power
9. Sweep frequency ±20% around resonance — does gas production peak
   at resonance?

### Experiment 4: Electrode Nucleation Effects (McAlister)
**Goal:** Test whether electrode surface treatment affects efficiency

**Materials:**
- Multiple electrode pairs: smooth, sandblasted, etched, nano-textured
- Same electrolyte and cell geometry for all
- Microscope or magnifying glass for surface inspection

**Procedure:**
1. Prepare electrodes with different surface treatments:
   - Polished smooth (600+ grit sandpaper)
   - Sandblasted (rough)
   - Acid-etched (muriatic acid, 30 seconds)
   - Scored with cross-hatch pattern
2. Run identical electrolysis on each pair
3. Measure: gas production rate, voltage, current
4. Observe: bubble size, bubble release rate (video if possible)
5. Rougher surfaces should release smaller bubbles more frequently —
   does this affect total gas yield per watt?

## Design Rules

1. **Measure power correctly.** This is the single most important rule.
   Bad power measurement is the #1 source of false claims.
2. **Always compare to DC baseline.** Any novel approach must beat steady
   DC at the same true input power.
3. **Control for temperature.** Electrolysis efficiency improves with
   temperature. If your novel approach heats the electrolyte, account for this.
4. **Use concentric tube geometry** for resonant cell testing — it creates
   a more uniform capacitance than flat plates.
5. **Electrolyte concentration matters.** Too dilute = high resistance.
   Too concentrated = corrosion and side reactions. 5-25% KOH is typical.

## Open Questions

1. Has anyone achieved a rigorous, independently verified demonstration of
   electrolysis efficiency beyond Faraday limits?
2. Does the Meyer cell's resonant frequency shift during operation (as gas
   bubbles change the effective dielectric constant)?
3. Can plasma electrolysis achieve better overall energy efficiency than
   conventional electrolysis, even though it requires higher voltage?
4. What is the role of the electrode-electrolyte interface in determining
   efficiency — is this where the interesting physics happens?
