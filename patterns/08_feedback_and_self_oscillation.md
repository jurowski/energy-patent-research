# Pattern 8: Feedback Loops & Self-Oscillation

**Prevalence:** 13 of 768 patents (1.7%) explicitly, but implicit in PAGD
self-pulsing, resonant systems, and back-EMF recovery circuits  
**Cross-cutting pattern that connects many other patterns**

## What It Is

Several high-efficiency energy patents describe systems that, once started,
partially or wholly sustain their own operation through feedback. This ranges
from mundane (regenerative braking in EVs) to exotic (self-running generators).

The key engineering question: can a system's output be fed back to its input
in a way that reduces net external power consumption while maintaining
useful work output?

## Types of Feedback in Energy Patents

### 1. Back-EMF Recovery (3 patents)
When current through an inductor is interrupted, the collapsing magnetic
field generates a voltage spike (back-EMF) that can be many times the
supply voltage. Most conventional circuits dissipate this energy in
snubber circuits or freewheeling diodes. Several patents specifically
capture this energy:

- **Gray motor (US3890548):** Recovery capacitor bank captures back-EMF
- **DE3021154A1 (Popescu):** Pulsed energy recovery system
- **CN110248849B:** Integrated hybrid energy recovery and storage

### 2. Regenerative Systems (Curtis Bradley, 4 patents)
Bradley's internal combustion engine patents (US3939806A, US4003204A, etc.)
use exhaust heat to regenerate fuel via a closed-loop thermochemical cycle.
Heat → working fluid → fuel regeneration → combustion → heat. This is
a legitimate thermodynamic cycle, not perpetual motion.

### 3. Self-Pulsing / Self-Oscillation
Some systems naturally oscillate without external timing:
- **PAGD (Correa):** Gas discharge self-pulses in the negative resistance regime
- **Certain resonant circuits:** Self-oscillating when Q > losses/cycle
- **Relaxation oscillators:** Neon lamps, UJTs, gas tubes charge/discharge cyclically

Self-oscillation occurs when a system has:
1. An energy storage mechanism (capacitor, inductor, spring)
2. A non-linear switching element (spark gap, plasma, saturating core)
3. A feedback path from output to input

### 4. Parametric Amplification
Varying a reactive component (capacitance or inductance) at twice the
resonant frequency can pump energy into a resonant circuit. This is
well-established physics (parametric oscillators are used in radio
astronomy). If the parameter variation comes from the system's own
oscillation, you have parametric self-oscillation.

## The Thermodynamic Reality Check

**No feedback loop creates energy from nothing.** But feedback can:
1. **Increase efficiency** by recovering waste energy (back-EMF, exhaust heat)
2. **Reduce input requirements** by recycling energy within the system
3. **Access non-obvious energy sources** by coupling to environmental fields,
   thermal gradients, or nuclear-scale phenomena
4. **Create resonant energy buildup** where small inputs produce large
   circulating energies

The question for each patent isn't "does it create energy?" but "does it
access and convert energy more efficiently than the conventional approach?"

## Actionable Design Principles

### Experiment 1: Back-EMF Energy Recovery Circuit
**Goal:** Measure what percentage of energy stored in an inductor can be
recovered via back-EMF capture

**Materials:**
- Inductor: 1mH, ferrite core (or hand-wound on toroid)
- MOSFET (IRFZ44N or similar)
- Arduino or 555 timer for gate drive
- Charge capacitor: 470µF, 50V
- Recovery capacitor: 470µF, 50V
- Fast recovery diode: UF4007
- Oscilloscope + current probe
- Precision voltage measurement

**Circuit:**
```
V_supply ──┬── [Charge Cap] ──┬── [MOSFET] ── [Inductor] ── GND
            │                  │
            │                  └── [Diode] ──── [Recovery Cap] ── GND
            │
            └── Voltage monitor
```

**Procedure:**
1. Charge the charge capacitor to known voltage (e.g., 20V)
2. Calculate stored energy: E₁ = ½CV²
3. Fire MOSFET for calculated time to fully transfer energy to inductor
   t = L × I_peak / V (where I_peak for full transfer: I = V × t / L)
4. Open MOSFET — back-EMF drives current through diode into recovery cap
5. Measure final voltage on recovery cap
6. Calculate recovered energy: E₂ = ½CV²
7. Recovery ratio: η = E₂/E₁

**Expected results:** With good components, η should be 70-90%. The losses
are in MOSFET resistance, diode drop, and ESR of capacitors.

**What would be anomalous:** η > 95% or any configuration where recovery
seems to exceed input. This would indicate energy coupling from another source.

### Experiment 2: Self-Oscillating LC Circuit
**Goal:** Build a circuit that self-oscillates using negative resistance

**Materials:**
- Neon lamp (NE-2 type, fires at ~65V, extinguishes at ~55V)
- Capacitor: 10nF
- Inductor: 10mH
- DC power supply: 0-100V (bench supply)
- Oscilloscope

**Circuit:**
```
V_supply ──── [R_ballast 100kΩ] ──┬── [Neon lamp] ── GND
                                   │
                                   ├── [Capacitor]
                                   │
                                   └── [Inductor]
```

**Procedure:**
1. Slowly increase voltage until neon lamp flickers (begins oscillating)
2. Monitor oscillation waveform on scope
3. The neon lamp acts as a negative resistance switch — charges cap until
   firing voltage, discharges through inductor, extinguishes, repeats
4. Measure: oscillation frequency, amplitude, input power
5. Vary: capacitor value, inductor value, supply voltage
6. This is the simplest demonstration of self-oscillation via negative
   resistance — same principle as the Correa PAGD

### Experiment 3: Parametric Oscillation
**Goal:** Demonstrate energy pumping via parameter variation

**Materials:**
- Variable capacitor (AM radio tuning cap, ~10-365pF)
- Inductor: 1mH
- Small DC motor to spin variable capacitor (or hand-turn)
- Oscilloscope

**Procedure:**
1. Form LC tank circuit with variable cap + inductor
2. Calculate resonant frequency at mid-capacitance
3. Spin the variable capacitor at 2× the resonant frequency
   (mechanical rotation varies capacitance periodically)
4. Monitor tank circuit voltage on scope
5. With correct timing, the voltage amplitude should GROW — energy is
   being pumped in by the mechanical variation of capacitance
6. This is parametric amplification. The energy comes from the motor
   turning the capacitor (mechanical → electrical conversion)

## Design Rules

1. **Capture every back-EMF spike.** In pulsed systems, the collapsing
   field energy is significant. Use fast diodes and recovery capacitors.
2. **Look for negative resistance.** Any device with a region where dV/dI < 0
   can potentially self-oscillate. This is your indicator of interesting physics.
3. **Match impedances for maximum energy transfer.** The feedback path must
   be impedance-matched to the source for efficient energy return.
4. **Self-oscillation frequency is diagnostic.** The frequency at which a
   system naturally oscillates tells you about its internal energy storage
   and dissipation characteristics.
5. **Don't confuse circulating energy with output energy.** A resonant
   system can have very high internal energy while producing modest output.
   Measure NET energy in/out, not peak circulating energy.

## Open Questions

1. Can back-EMF recovery exceed conventional expectations when combined
   with non-linear elements (spark gaps, plasma switches)?
2. Does the switching element affect recovery efficiency in ways not
   predicted by linear circuit theory?
3. Can parametric oscillation be driven by the system's own fields
   (e.g., magnetic field from the inductor physically moving a capacitor
   plate)?
4. What is the maximum theoretical feedback ratio for each topology?
