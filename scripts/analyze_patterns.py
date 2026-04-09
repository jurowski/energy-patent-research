"""
Analyze patent database for recurring technical patterns.

Usage:
    python3 analyze_patterns.py
"""

import sqlite3
import re
from collections import Counter
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "patents.db"


def get_all_patents(conn):
    c = conn.cursor()
    c.execute("SELECT patent_number, title, abstract, inventor, category, notes FROM patents")
    cols = [d[0] for d in c.description]
    return [dict(zip(cols, row)) for row in c.fetchall()]


def analyze_keyword_frequency(patents):
    """Find most common technical terms across all titles and abstracts."""
    # Technical terms to look for
    tech_terms = [
        "resonan", "puls", "magnetic", "coil", "toroid", "bifilar",
        "capacitor", "inductor", "frequency", "oscillat", "harmonic",
        "impedance", "flux", "permanent magnet", "back.?EMF", "counter.?EMF",
        "radiant", "scalar", "longitudinal", "transverse",
        "zero.?point", "vacuum", "quantum", "casimir",
        "dielectric", "ferrite", "neodymium", "rare earth", "bismuth",
        "barium", "titanate", "piezo", "crystal",
        "electrolysis", "hydrogen", "oxygen", "water split",
        "plasma", "glow discharge", "arc", "spark gap",
        "excess heat", "anomalous", "over.?unity", "COP",
        "self.?sustain", "self.?run", "feedback", "regenerat",
        "phase", "standing wave", "node", "antinode",
        "vortex", "implosion", "cavitat", "sonoluminescen",
        "nuclear", "transmut", "fusion", "fission",
        "palladium", "deuterium", "nickel", "lithium",
        "thermionic", "thermoelectric", "photovoltaic",
        "superconductor", "superconduct",
        "scalar wave", "torsion field", "aether", "ether",
        "rodin", "fibonacci", "golden ratio", "sacred geometry",
        "switched reluctance", "homopolar", "unipolar",
    ]

    counts = Counter()
    for p in patents:
        text = f"{p.get('title', '')} {p.get('abstract', '')} {p.get('notes', '')}".lower()
        for term in tech_terms:
            if re.search(term, text):
                counts[term] += 1

    return counts


def analyze_inventor_overlap(patents):
    """Find inventors who appear multiple times or across categories."""
    inventor_patents = {}
    for p in patents:
        inv = p.get("inventor", "")
        if not inv:
            continue
        if inv not in inventor_patents:
            inventor_patents[inv] = []
        inventor_patents[inv].append(p)

    # Inventors with multiple patents
    multi = {k: v for k, v in inventor_patents.items() if len(v) > 1}
    return multi


def analyze_common_features(patents):
    """Look for common technical approaches across patents."""
    features = {
        "uses_resonance": [],
        "uses_pulsed_dc": [],
        "uses_back_emf_recovery": [],
        "uses_special_coil_geometry": [],
        "uses_permanent_magnets": [],
        "uses_capacitor_discharge": [],
        "uses_high_voltage": [],
        "uses_water_splitting": [],
        "uses_plasma_discharge": [],
        "claims_excess_energy": [],
        "uses_feedback_loop": [],
        "uses_specific_frequency": [],
        "uses_special_materials": [],
        "uses_magnetic_flux_control": [],
    }

    patterns = {
        "uses_resonance": r"resonan|tuned circuit|LC circuit|tank circuit",
        "uses_pulsed_dc": r"puls|impulse|sharp edge|duty cycle|square wave",
        "uses_back_emf_recovery": r"back.?EMF|counter.?EMF|flyback|energy recover|recaptur",
        "uses_special_coil_geometry": r"bifilar|toroid|caduceus|pancake coil|flat coil|wound|winding",
        "uses_permanent_magnets": r"permanent magnet|neodymium|rare earth|ferrite magnet|NdFeB",
        "uses_capacitor_discharge": r"capacitor discharge|capacitive|charge.{0,20}discharge",
        "uses_high_voltage": r"high voltage|kilovolt|kV|high potential",
        "uses_water_splitting": r"electrolysis|water split|hydrogen generat|HHO|Brown.?s gas|water fuel",
        "uses_plasma_discharge": r"plasma|glow discharge|arc discharge|spark|ioniz",
        "claims_excess_energy": r"over.?unity|excess|anomalous|COP.{0,10}[2-9]|greater than|more.{0,20}than.{0,20}input|free energy",
        "uses_feedback_loop": r"feedback|self.?sustain|self.?run|regenerat|closed loop",
        "uses_specific_frequency": r"\d+\s*(Hz|kHz|MHz|GHz)|frequency|tuned|hertz",
        "uses_special_materials": r"bismuth|barium titanate|piezo|crystal|metamaterial|graphene|superconductor",
        "uses_magnetic_flux_control": r"flux switch|flux path|magnetic circuit|flux control|reluctance",
    }

    for p in patents:
        text = f"{p.get('title', '')} {p.get('abstract', '')} {p.get('notes', '')}".lower()
        for feature, pattern in patterns.items():
            if re.search(pattern, text):
                features[feature].append(p["patent_number"])

    return features


def main():
    conn = sqlite3.connect(DB_PATH)
    patents = get_all_patents(conn)
    print(f"Analyzing {len(patents)} patents...\n")

    # 1. Keyword frequency
    print("=" * 70)
    print("TOP TECHNICAL TERMS (appearing in title/abstract/notes)")
    print("=" * 70)
    counts = analyze_keyword_frequency(patents)
    for term, count in counts.most_common(40):
        bar = "█" * min(count, 50)
        pct = count / len(patents) * 100
        print(f"  {term:25s} {count:4d} ({pct:5.1f}%) {bar}")

    # 2. Feature analysis
    print(f"\n{'=' * 70}")
    print("COMMON TECHNICAL FEATURES")
    print("=" * 70)
    features = analyze_common_features(patents)
    for feature, patent_nums in sorted(features.items(), key=lambda x: -len(x[1])):
        count = len(patent_nums)
        pct = count / len(patents) * 100
        bar = "█" * min(count, 50)
        print(f"  {feature:35s} {count:4d} ({pct:5.1f}%) {bar}")

    # 3. Feature co-occurrence
    print(f"\n{'=' * 70}")
    print("FEATURE CO-OCCURRENCE (patents exhibiting both features)")
    print("=" * 70)
    feature_names = list(features.keys())
    cooccurrences = []
    for i, f1 in enumerate(feature_names):
        s1 = set(features[f1])
        for f2 in feature_names[i + 1:]:
            s2 = set(features[f2])
            overlap = s1 & s2
            if len(overlap) >= 3:
                cooccurrences.append((f1, f2, len(overlap)))

    for f1, f2, count in sorted(cooccurrences, key=lambda x: -x[2])[:20]:
        print(f"  {f1:35s} + {f2:35s} = {count:3d} patents")

    # 4. Multi-patent inventors
    print(f"\n{'=' * 70}")
    print("INVENTORS WITH MULTIPLE PATENTS")
    print("=" * 70)
    multi = analyze_inventor_overlap(patents)
    for inv, pats in sorted(multi.items(), key=lambda x: -len(x[1]))[:15]:
        categories = set(p.get("category", "?") for p in pats)
        print(f"  {inv[:40]:40s} {len(pats):3d} patents | categories: {', '.join(categories)}")

    # 5. Top patterns summary
    print(f"\n{'=' * 70}")
    print("SYNTHESIS: MOST COMMON TECHNICAL PATTERNS")
    print("=" * 70)

    top_features = sorted(features.items(), key=lambda x: -len(x[1]))[:8]
    for rank, (feature, patent_nums) in enumerate(top_features, 1):
        count = len(patent_nums)
        pct = count / len(patents) * 100
        print(f"\n  {rank}. {feature.replace('_', ' ').upper()} — {count} patents ({pct:.1f}%)")

        # Show a few example patents
        for pn in patent_nums[:3]:
            p = next((x for x in patents if x["patent_number"] == pn), None)
            if p:
                print(f"     Example: {pn} — {p.get('title', '?')[:55]}")

    conn.close()


if __name__ == "__main__":
    main()
