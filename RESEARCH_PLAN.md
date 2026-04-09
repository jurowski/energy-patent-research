# Research Plan

## Phase 1: Identify the Patent Landscape

### 1a. Categories of interest
Energy devices where inventors have claimed unusually high efficiency or
unconventional energy conversion. Key categories:

| Category | What to look for |
|---|---|
| **Electromagnetic generators** | Over-unity claims, novel coil geometries, magnetic flux path innovations, resonance-based power extraction |
| **Electrochemical cells** | Anomalous excess heat, cold fusion / LENR patents, novel electrolyte systems |
| **Solid-state devices** | Casimir effect harvesting, zero-point energy claims, thermionic converters with unusual materials |
| **Thermodynamic engines** | Claims exceeding Carnot limits, novel thermodynamic cycles, waste heat recovery at unusual efficiency |
| **Plasma / discharge devices** | Plasma electrolysis, water dissociation with anomalous efficiency, high-voltage discharge devices |
| **Piezoelectric / vibrational** | Ambient energy harvesting beyond expected thresholds |

### 1b. Key inventors and patent holders to research
Known inventors whose work has been associated with high-efficiency claims
or has attracted secrecy orders / suppression narratives:

- **T. Henry Moray** — radiant energy device (1920s-30s)
- **Stanley Meyer** — water fuel cell (US4936961)
- **Edwin Gray** — EMA motor (US3890548, US4595975)
- **Joseph Newman** — energy machine (patent denied, published book)
- **John Bedini** — battery charging / motor systems
- **Floyd Sweet** — vacuum triode amplifier (no patent filed)
- **Paulo & Alexandra Correa** — PAGD reactor (US5,449,989)
- **Randell Mills / Brilliant Light Power** — hydrino theory patents
- **Andrea Rossi** — E-Cat (LENR device)
- **Thomas Valone** — homopolar generator research
- **Nikola Tesla** — numerous relevant patents (radiant energy, magnifying transmitter)
- **Viktor Schauberger** — implosion technology
- **John Searl** — Searl Effect Generator
- **Paramahamsa Tewari** — space vortex theory / RLG

### 1c. FOIA & secrecy order data
- FOIA requests to USPTO for counts of active secrecy orders by patent class
- Federation of American Scientists tracks secrecy order statistics
  (historically 5,000-6,000 active orders at any time)
- Patent classes most frequently hit: nuclear, cryptography, but also
  some energy conversion classes

## Phase 2: Extract & Catalog Patent Data

For each patent identified:
- Patent number, filing date, grant date, current status
- Inventor(s), assignee(s)
- IPC/CPC classification codes
- Abstract and key claims
- Efficiency claims (if any)
- Key technical features (materials, geometries, frequencies, etc.)
- Whether secrecy order was ever applied
- Cited/citing patents (build a citation graph)
- Outcome: was device ever independently replicated?

Store in `data/patents.db` (SQLite).

## Phase 3: Pattern Analysis

Look for recurring themes across the catalog:

### Technical commonalities to investigate
1. **Resonance** — do many devices exploit electrical, mechanical, or acoustic resonance?
2. **Non-linear magnetics** — amorphous core materials, specific B-H curve shapes?
3. **Pulsed DC vs. AC** — do high-efficiency claims correlate with pulsed/impulse waveforms?
4. **Specific frequencies** — any clustering around particular frequencies?
5. **Material choices** — barium titanate, bismuth, rare earths, specific alloys?
6. **Geometric patterns** — toroidal, bifilar, caduceus coil configurations?
7. **Phase relationships** — specific phase angles between fields?
8. **Self-oscillation** — feedback loops creating self-sustaining oscillation?
9. **Environmental coupling** — devices that seem to interact with ambient fields?
10. **Thermal anomalies** — excess heat or unexpected cooling?

### Analytical methods
- Cluster analysis on patent text (NLP / topic modeling)
- Citation network analysis
- Timeline analysis (when do similar ideas independently appear?)
- Cross-reference with secrecy order patent classes

## Phase 4: Synthesize Open Designs

Based on identified patterns:
1. Design simple, reproducible experiments to test each principle
2. Specify with commodity/available parts
3. Define clear measurement protocols
4. Publish everything openly (Creative Commons)
5. Build community for independent replication

## Phase 5: Build & Test

- Prototype the most promising configurations
- Document rigorously with video, data logging
- Share all results (positive AND negative)
- Iterate based on community feedback
