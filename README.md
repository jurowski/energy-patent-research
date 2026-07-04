# energy-patent-research

Open-source research project analyzing **768 publicly-available energy device patents** to identify common technical principles, topologies, and materials among devices claiming high efficiency or unconventional energy conversion.

All findings published openly — **no patents, no secrets, no paywalls.**

## What's in this repo

| Path | Contents |
|---|---|
| `data/patents.db` | SQLite database of 768 patents (title, abstract, filing/grant dates, inventor, assignee, IPC/CPC codes, claims, efficiency claims, key features, category) plus citations and tags tables. Scraped from public sources. |
| `research/` | Per-category research notes: `electrochemical/`, `electromagnetic/`, `plasma/`, `solid-state/`, `thermodynamic/`, `suppressed-or-classified/` |
| `patterns/` | The **10 recurring technical patterns** identified across the corpus — coil geometry, pulsed DC, resonance, plasma discharge, magnet topologies, anomalous water splitting, LENR, feedback/self-oscillation, special materials, and the synthesis that combines them. Each file includes patents referenced, underlying physics, and actionable bench experiments with materials lists. Start at [`patterns/README.md`](patterns/README.md). |
| `designs/` | Open-source device concepts derived from pattern analysis (work in progress) |
| `scripts/fetch_patents.py` | Regenerates `data/patents.db` from public patent sources (USPTO / Google Patents / EPO / WIPO). Stdlib only. |
| `scripts/analyze_patterns.py` | Regex keyword-frequency analysis (the original, hypothesis-shaped pass). Stdlib only. |
| `scripts/enrich_patents.py` | Backfills full `claims_text` (scrape) + `efficiency_claims` / `key_features` (LLM read). Needs an API key — see [Enriching the corpus](#enriching-the-corpus). |
| `scripts/semantic_clusters.py` | Model-read cross-patent synthesis — supersedes `analyze_patterns.py`; writes `patterns/11_semantic_synthesis.md`. Needs an API key. |
| `scripts/anthropic_batch.py` | Shared Message Batches helper used by the two scripts above. |
| `requirements.txt` | Python deps for the enrichment scripts (just `anthropic`). |
| `RESEARCH_PLAN.md` | Overall goals + methodology |
| `CLAUDE.md` | Project brief for AI assistants working on this repo |

## Quickstart

```bash
git clone https://github.com/jurowski/energy-patent-research.git
cd energy-patent-research

# The database is committed — open it directly
sqlite3 data/patents.db

# Or regenerate from source (requires Python + the public patent APIs)
python scripts/fetch_patents.py
```

### Query the database

```sql
-- Distribution by category
SELECT category, COUNT(*) AS n
FROM patents
GROUP BY category
ORDER BY n DESC;

-- Patents that claim >100% efficiency
SELECT patent_number, title, efficiency_claims
FROM patents
WHERE efficiency_claims LIKE '%over%unity%'
   OR efficiency_claims LIKE '%100%';
```

## Enriching the corpus

The committed `patents.db` is thin — title, a one-sentence abstract, dates, and
codes. `claims_text`, `efficiency_claims`, and `key_features` are empty. Two
optional scripts deepen it and run a model-read analysis in place of the regex
pass. They call the Anthropic API, so they need a key and one dependency:

```bash
pip install -r requirements.txt

# Auth: the SDK reads ANTHROPIC_API_KEY (or an `ant auth login` profile).
# Nothing is stored in the repo — "no secrets" still holds.
export ANTHROPIC_API_KEY=sk-ant-...

# 1. Backfill claims (scrape, stdlib) then extracted fields (LLM). --batch = 50% cheaper, async.
python scripts/enrich_patents.py --fetch
python scripts/enrich_patents.py --extract --batch

# 2. Model-read fingerprints → cross-patent synthesis (patterns/11_semantic_synthesis.md)
python scripts/semantic_clusters.py --map --batch
python scripts/semantic_clusters.py --reduce

# Trial the LLM steps on a handful of rows first: add --limit 15
```

The scrape legitimately fails on pre-1976 patents with no OCR'd full text (Tesla
et al.) — those stay null and are recorded, not fatal. All **outputs** (enriched
DB, `data/fingerprints.json`, the synthesis file) stay open under CC BY-SA, same
as everything else here — only the tooling needs a key.

## The Meta-Pattern (corrected 2026-07)

The original keyword analysis proposed a three-element recipe — *non-linear +
resonance + pulsed excitation*. A mechanism-level re-read of the enriched corpus
(766 of 768 patents fingerprinted) found that combination in only **13 patents**,
and only **6** of those claim an anomalous effect: **the recipe was largely a
keyword artifact.** 72% of the corpus has no non-linear element; 83% has no
resonance.

The real anomalous signal is **independent-inventor convergence** — the same
mechanism template reached by unrelated filers across decades and countries.
~101 patents claim a genuinely anomalous effect, clustering into a few templates:
Casimir / ambient-EM → DC, resonant water dissociation, back-EMF recovery loops,
and metal-hydride LENR excess heat.

See [`patterns/11_semantic_synthesis.md`](patterns/11_semantic_synthesis.md) for
the model-read analysis and [`patterns/12_revised_experiment_priorities.md`](patterns/12_revised_experiment_priorities.md)
for the revised, falsification-first experiment ranking (6 experiments, ~$30–200
each). Patterns 1–10 are retained for provenance; the original 29 experiments
remain valid as component-characterization work.

## How this feeds into HiveJournal

This repo is pinned as a git submodule inside [`hivejournal-2026`](https://github.com/jurowski/hivejournal-2026) at `vendor/energy-patent-research/`. HiveJournal's `scripts/import-energy-patents.ts` reads directly from:

- `data/patents.db` → seeds the **Patents** notebook (768 entries, one per patent)
- `patterns/*.md` → seeds the **Experiments** notebook (29 original + 6 revised-priority experiment entries cross-referencing their source patents)

Those notebooks power the [hivejournal.com/open-energy](https://hivejournal.com/open-energy) 10-phase pathway, the Constellation view, and the Cheer Dashboard. This repo is the upstream data pipeline; HiveJournal is the product surface.

## Contributing

New findings, additional patents, corrections, and bench-test results from the `patterns/` experiments are all welcome.

- Open an issue for discussion first on anything speculative.
- PRs should cite public sources and include reproducible steps.
- Keep the "no secrets" principle — if you can't link to a public source, it doesn't go in.

## License

[CC BY-SA 4.0](LICENSE) — share freely with attribution and under the same terms.
