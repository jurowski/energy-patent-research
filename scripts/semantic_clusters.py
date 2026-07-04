"""
Semantic replacement for analyze_patterns.py.

The old analyzer counts occurrences of a hardcoded ~90-term list over titles and
one-sentence abstracts. That's confirmation-shaped: the term list already encodes
the "resonance + pulsed + non-linear" thesis, so the output confirms it, and it
is blind to any structure nobody thought to add to the list.

This does two model-read passes over the *enriched* corpus instead:

  MAP     Claude reads each patent's claims and assigns a structured mechanism
          fingerprint from a controlled vocabulary — the model fills the slots by
          reading, rather than a regex matching surface strings. Cached to
          data/fingerprints.json so the (expensive) map runs once.

  REDUCE  A single high-effort Claude call reads ALL fingerprints together
          (768 small records ≈ well under 100K tokens — one context window) and
          writes the cross-patent synthesis: which mechanism combinations recur,
          which are rare-but-repeated (the whitespace worth prototyping), inventor
          lineage across mechanisms, and ranked candidate device concepts with the
          specific patents motivating each. Output: patterns/11_semantic_synthesis.md
          (a NEW file — it does not overwrite the regex-derived 01–10).

    python3 semantic_clusters.py --map          # build fingerprints (once)
    python3 semantic_clusters.py --reduce        # synthesize the report
    python3 semantic_clusters.py --map --reduce  # both
    python3 semantic_clusters.py --map --limit 15  # cheap trial first

Requires enrich_patents.py to have run (claims_text / key_features populated) and
`pip install anthropic`. Auth resolves from the environment / `ant auth login`.
"""

import argparse
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "patents.db"
FP_PATH = Path(__file__).parent.parent / "data" / "fingerprints.json"
OUT_PATH = Path(__file__).parent.parent / "patterns" / "11_semantic_synthesis.md"

MAP_MODEL = "claude-opus-4-8"        # cheap-ish per-patent read; low effort
REDUCE_MODEL = "claude-opus-4-8"     # the reasoning-heavy step — point at claude-fable-5 if you want the frontier

# Controlled vocabulary. The MODEL fills these by reading the claims; that is the
# whole point — the slots are structural, not keyword triggers. Extend the enums
# as the corpus teaches you new categories.
FINGERPRINT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "energy_input": {"type": "string", "enum": [
            "electrical_pulsed", "electrical_resonant", "electrical_dc",
            "magnetic_static", "chemical", "thermal", "mechanical",
            "plasma_discharge", "nuclear_lattice", "ambient_em", "unclear"]},
        "nonlinear_element": {"type": "string", "enum": [
            "saturating_core", "plasma_gap", "ferroelectric",
            "semiconductor_junction", "spark_gap", "none", "unclear"]},
        "resonance": {"type": "string", "enum": [
            "electrical_lc", "mechanical", "acoustic", "cavity", "none", "unclear"]},
        "excitation": {"type": "string", "enum": [
            "pulsed_sharp_edge", "capacitor_discharge", "sinusoidal",
            "dc", "impulse", "none", "unclear"]},
        "claimed_effect": {"type": "string", "enum": [
            "over_unity", "excess_heat", "anomalous_gas_yield",
            "self_sustaining", "waste_heat_recovery", "conventional", "unclear"]},
        "couples_to_ambient_field": {"type": "boolean"},
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
        "mechanism_summary": {"type": "string",
            "description": "One sentence, grounded in the claims, on how it is claimed to work."},
    },
    "required": ["energy_input", "nonlinear_element", "resonance", "excitation",
                 "claimed_effect", "couples_to_ambient_field", "confidence",
                 "mechanism_summary"],
}

MAP_SYSTEM = (
    "You read one energy-device patent and classify its *mechanism* into the given "
    "schema by reading the claims. Choose 'unclear' rather than guessing when the "
    "text does not support a slot. Set confidence honestly — 'low' when you only had "
    "a title and short abstract to work from."
)

REDUCE_SYSTEM = (
    "You are a research analyst looking for genuine cross-patent structure in a "
    "corpus of energy-device patents, most making unconventional efficiency claims. "
    "You are given a structured mechanism fingerprint for every patent. Find real "
    "patterns, not the ones someone hoped to find. Distinguish (a) common "
    "combinations from (b) rare-but-recurring combinations — the second set is the "
    "more interesting whitespace. Ground every claim in specific patent numbers. Be "
    "candid about what the data cannot support; low-confidence fingerprints are weak "
    "evidence. Lead with the outcome. Do not invent patents or numbers."
)


def _fable_kwargs(model: str) -> dict:
    if model.startswith("claude-fable") or model.startswith("claude-mythos"):
        return {"betas": ["server-side-fallback-2026-06-01"],
                "fallbacks": [{"model": "claude-opus-4-8"}]}
    return {}


def _map_params(patent: dict, model: str) -> dict:
    """messages.create kwargs for one fingerprint — shared by threaded + batch paths."""
    source = patent.get("claims_text") or (
        f"TITLE: {patent.get('title','')}\nFEATURES: {patent.get('key_features','')}\n"
        f"EFFICIENCY: {patent.get('efficiency_claims','')}")
    return {
        "model": model,
        "max_tokens": 1200,
        "system": MAP_SYSTEM,
        "output_config": {"effort": "low",
                          "format": {"type": "json_schema", "schema": FINGERPRINT_SCHEMA}},
        "messages": [{"role": "user",
                      "content": f"Patent {patent['patent_number']}:\n\n{source[:24000]}"}],
    }


def _finish_fp(fp: dict, patent: dict) -> dict:
    fp.update({"patent_number": patent["patent_number"], "title": patent["title"],
               "category": patent["category"], "inventor": patent["inventor"]})
    return fp


def run_map(model: str, limit: int | None, concurrency: int, use_batch: bool) -> None:
    from anthropic import Anthropic

    client = Anthropic()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    q = ("SELECT patent_number, title, category, inventor, claims_text, "
         "key_features, efficiency_claims FROM patents")
    if limit:
        q += f" LIMIT {int(limit)}"
    rows = [dict(r) for r in conn.execute(q).fetchall()]
    conn.close()
    print(f"MAP: fingerprinting {len(rows)} patents ({model})...\n")

    fingerprints, errors = [], 0

    if use_batch:
        if _fable_kwargs(model):
            print("  (batch + Fable: no server-side fallbacks — refusals surface as null results)")
        from anthropic_batch import submit_and_collect

        idmap = {f"p{i}": p for i, p in enumerate(rows)}
        reqs = [{"custom_id": cid, "params": _map_params(p, model)} for cid, p in idmap.items()]
        for cid, msg in submit_and_collect(client, reqs, label="map").items():
            p = idmap[cid]
            if msg is None:
                errors += 1
                continue
            fp = json.loads(next((b.text for b in msg.content if b.type == "text"), "{}"))
            fingerprints.append(_finish_fp(fp, p))
    else:
        def work(p):
            create = client.beta.messages.create if _fable_kwargs(model) else client.messages.create
            try:
                resp = create(**_map_params(p, model), **_fable_kwargs(model))
                fp = json.loads(next((b.text for b in resp.content if b.type == "text"), "{}"))
                return _finish_fp(fp, p)
            except Exception as e:  # noqa: BLE001
                return {"patent_number": p["patent_number"], "_error": str(e)}

        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            for i, fp in enumerate(
                (f.result() for f in as_completed(pool.submit(work, p) for p in rows)), 1
            ):
                if "_error" in fp:
                    errors += 1
                    print(f"  [{i}/{len(rows)}] {fp['patent_number']:18s} ERROR {fp['_error'][:50]}")
                else:
                    fingerprints.append(fp)
                    print(f"  [{i}/{len(rows)}] {fp['patent_number']:18s} "
                          f"{fp['energy_input']}/{fp['claimed_effect']} ({fp['confidence']})")

    FP_PATH.write_text(json.dumps(fingerprints, indent=2))
    print(f"\nMAP done: {len(fingerprints)} fingerprints → {FP_PATH} ({errors} errors)")


def run_reduce(model: str) -> None:
    from anthropic import Anthropic

    if not FP_PATH.exists():
        raise SystemExit("No fingerprints.json — run --map first.")
    fingerprints = json.loads(FP_PATH.read_text())
    print(f"REDUCE: synthesizing over {len(fingerprints)} fingerprints ({model})...\n")

    client = Anthropic()
    prompt = (
        "Here is the mechanism fingerprint for every patent in the corpus, as JSON. "
        "Write a synthesis in Markdown with these sections:\n"
        "1. What the corpus actually shows (the honest top-line, hedged by confidence).\n"
        "2. Common mechanism combinations, each with a count and 3-5 example patent numbers.\n"
        "3. Rare-but-recurring combinations — the whitespace — with the patents and why they're interesting.\n"
        "4. Inventor lineage: inventors whose patents span multiple mechanism classes.\n"
        "5. Ranked candidate device concepts to prototype, each naming the specific "
        "patents that motivate it and the single cheapest bench test that would falsify it.\n\n"
        f"FINGERPRINTS:\n{json.dumps(fingerprints)}"
    )
    # Streaming + generous max_tokens because the report is long; adaptive thinking
    # + high effort because this is the reasoning-heavy step.
    with client.messages.stream(
        model=model,
        max_tokens=32000,
        system=REDUCE_SYSTEM,
        thinking={"type": "adaptive"},
        output_config={"effort": "xhigh"},
        messages=[{"role": "user", "content": prompt}],
        **_fable_kwargs(model),
    ) as stream:
        msg = stream.get_final_message()

    report = "".join(b.text for b in msg.content if b.type == "text")
    OUT_PATH.write_text(
        "# Pattern 11 — Semantic Synthesis (model-read)\n\n"
        "_Generated by `scripts/semantic_clusters.py` from model-read mechanism "
        "fingerprints, not keyword counts. Companion to 01–10; supersedes the "
        "regex-derived pattern detection in `analyze_patterns.py`._\n\n"
        + report + "\n"
    )
    print(f"REDUCE done → {OUT_PATH}")


def main():
    ap = argparse.ArgumentParser(description="Model-read cross-patent synthesis")
    ap.add_argument("--map", action="store_true", help="Build per-patent fingerprints")
    ap.add_argument("--reduce", action="store_true", help="Synthesize the report")
    ap.add_argument("--limit", type=int, help="Only fingerprint N patents (trial)")
    ap.add_argument("--map-model", default=MAP_MODEL)
    ap.add_argument("--reduce-model", default=REDUCE_MODEL)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--batch", action="store_true",
                    help="Run the MAP step via Message Batches API (50%% cheaper, async)")
    args = ap.parse_args()

    if not (args.map or args.reduce):
        ap.error("pick at least one of --map / --reduce")
    if args.map:
        run_map(args.map_model, args.limit, args.concurrency, args.batch)
    if args.reduce:
        run_reduce(args.reduce_model)


if __name__ == "__main__":
    main()
