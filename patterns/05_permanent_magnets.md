# Pattern 5: Permanent Magnet Topologies

**Prevalence:** 50 of 768 patents (6.5%)  
**Categories:** Primarily electromagnetic  
**Co-occurrence:** Coil geometry (19 — strongest combo in database), flux control (7), excess energy claims (3)

## What It Is

Permanent magnets — particularly high-energy rare earth magnets (NdFeB) —
appear extensively in high-efficiency energy device patents. The key is not
just *using* magnets, but using them in specific arrangements designed to
create asymmetric, switched, or concentrated magnetic fields.

## Why Permanent Magnets Are Central

### 1. They Provide "Free" Magnetic Field
A permanent magnet maintains its field without continuous energy input. The
energy is stored in the aligned magnetic domains from the manufacturing
process. This means a permanent magnet can do work (attract/repel, induce
EMF) without drawing from an external power source.

### 2. The Asymmetry Question
Several patents attempt to create asymmetric magnetic circuits — where
the force or flux in one direction is greater than the other. In a
perfectly symmetric system, the net work over a full cycle is zero (you
push as hard pulling back as pushing forward). But if the magnetic circuit
can be switched between high and low permeability states, asymmetry
may be achievable.

### 3. Halbach Arrays and Flux Concentration
Halbach arrays arrange magnets so that the field is concentrated on one
side and nearly cancelled on the other. This is well-established physics
(used in particle accelerators and modern motors). The relevant principle:
you can shape magnetic fields to be much stronger in one region than
predicted by a single magnet's field alone.

## Key Configurations Found in Patents

### 1. Switched Reluctance / Flux Switching
**9 patents in database**

Permanent magnets embedded in a stator, with a toothed rotor that
changes the reluctance (magnetic resistance) of the circuit as it turns.
The flux path switches between different routes through the stator,
inducing EMF in the coils.

**Why it's interesting:** The magnet's energy is constant, but the flux
through the coils varies as the rotor turns. The rotor requires minimal
torque to turn (it's just changing the flux path, not fighting against
the magnet directly).

Key patents: CN106972730A, CN101820192B, CN103715848A

### 2. Magnetic Collapse / Sudden Flux Change
**WO2023239247A1 (Illanes)**

This patent combines permanent magnets with bifilar coils and pulsed DC.
The concept: suddenly removing or redirecting a magnet's flux through a
coil. The rate of flux change (dΦ/dt) determines induced voltage. If you
can cause a very rapid flux change (magnetic "collapse"), you generate a
high-voltage impulse.

### 3. Radial Electromagnetic Arrays
**US9716424B2 (Stoltenberg)**

Multiple arrays of linear motors/generators in a radial configuration.
Permanent magnets provide the field; coil arrays extract power. The claim
is high mechanical-to-electrical efficiency through the array geometry.

### 4. Memory Motors
**CN109194078B and related Chinese patents**

Motors where the permanent magnets can be partially magnetized or
demagnetized by a brief current pulse. This allows the motor's magnetic
characteristics to be changed on-the-fly without continuous power draw.
"Set and forget" field control.

## The Coil + Magnet Synergy (19 Patents)

The strongest co-occurrence in our entire database is coil geometry +
permanent magnets. This isn't surprising — motors and generators use both.
But the specific combinations are instructive:

- **Bifilar coils + magnets:** The bifilar coil's self-resonant behavior
  interacts with the magnet's field. At resonance, the coil's effective
  impedance changes dramatically.
- **Toroidal geometry + magnets:** Containment of flux within the toroid
  combined with external magnet field creates interesting boundary conditions.
- **Flux switching topologies:** Magnets provide steady field; coils pick
  up the time-varying component as the flux path is switched.

## Actionable Design Principles

### Experiment 1: Flux Switching Motor/Generator
**Goal:** Build a simple flux-switching generator and measure efficiency

**Materials:**
- Stator: Laminated steel or ferrite E-cores (2-4 pieces)
- Permanent magnets: N42 or N52 NdFeB blocks, 10×10×20mm
- Rotor: Toothed steel disc (can be laser-cut or hand-filed from mild steel)
- Magnet wire for coils (22-26 AWG)
- Small DC motor to spin rotor (or hand crank for low-speed testing)
- Oscilloscope + multimeter

**Procedure:**
1. Assemble stator with magnets embedded between E-cores
2. Wind pickup coils on E-core legs
3. Mount toothed rotor to pass through air gap
4. Spin rotor at known RPM
5. Measure: open-circuit voltage waveform, frequency, and amplitude
6. Add load resistors and measure power output vs RPM
7. Measure input torque (spring scale on motor arm, or measure motor
   electrical input if using DC drive motor)
8. Calculate: electrical output / mechanical input = efficiency

### Experiment 2: Halbach Array Field Mapping
**Goal:** Verify flux concentration and map the field of a Halbach array

**Materials:**
- 8-12 NdFeB cube magnets, 10mm (same grade)
- 3D-printed or wooden holder to maintain orientation
- Hall effect sensor (A1302 or similar linear sensor, ~$2)
- Arduino + analog input for reading sensor
- Graph paper for mapping grid

**Procedure:**
1. Arrange magnets in Halbach pattern (rotate each by 90° relative to neighbor)
2. Map field strength at 1cm grid points on strong side and weak side
3. Compare to same number of magnets all oriented the same direction
4. Quantify: field concentration ratio (strong side max / weak side max)
5. Halbach should show ~1.4× field on strong side, near-zero on weak side

### Experiment 3: Magnetic Field "Collapse" Pulse Generation
**Goal:** Generate voltage pulses by rapid flux switching through a coil

**Materials:**
- Strong NdFeB magnet on a rotating disc or linear slider
- Pickup coil wound on ferrite core
- Steel shunt (a piece of steel that can redirect flux)
- Solenoid actuator to rapidly insert/remove the shunt
- Oscilloscope

**Procedure:**
1. Position magnet so its flux passes through pickup coil via ferrite core
2. Measure steady flux (Hall sensor) and baseline coil voltage (≈0V DC)
3. Rapidly insert steel shunt to redirect flux away from coil
4. Measure induced voltage pulse on scope
5. Vary: shunt insertion speed, coil turns, core material
6. Key question: How does the pulse voltage scale with dΦ/dt?

## Design Rules

1. **Maximize dΦ/dt, not Φ.** Voltage is induced by *changing* flux, not
   by static flux. Design for rapid flux transitions.
2. **Use flux switching, not magnet motion.** Moving a magnet is slow;
   switching the flux path through fixed magnets is fast.
3. **Rare earth magnets are worth the cost.** N42-N52 NdFeB magnets have
   5-10× the energy product of ferrite. The stronger the field, the more
   pronounced any switching effects.
4. **Air gaps are the enemy of flux.** Minimize air gaps in the magnetic
   circuit. Every mm of air gap requires ~1000× more MMF than the same
   length of steel.
5. **Memory motor concept:** A brief current pulse can partially
   demagnetize/remagnetize certain magnet materials. This is "programmable"
   magnetic field strength with zero steady-state power.

## Open Questions

1. Can a flux-switching topology achieve generator efficiency significantly
   above conventional generators? (Conventional is ~85-95%)
2. Is the "magnetic collapse" patent (Illanes WO2023239247A1) replicable,
   and does the bifilar coil add measurable benefit over a conventional coil?
3. Can Halbach arrays improve generator output enough to justify the
   manufacturing complexity?
4. What happens when you combine flux switching with resonant coils — does
   driving the coil at resonance amplify the flux-switching effect?
