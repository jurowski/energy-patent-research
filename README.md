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
| `scripts/fetch_patents.py` | Regenerates `data/patents.db` from public patent sources (USPTO / Google Patents / EPO / WIPO) |
| `scripts/analyze_patterns.py` | Runs the cross-patent analysis that produced the `patterns/` files |
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

## The Meta-Pattern

The most promising devices across the corpus share three elements:

1. **Non-linear element** — saturating magnetic core, plasma gap, ferroelectric
2. **Resonance** — LC circuit, mechanical, or acoustic
3. **Pulsed excitation** — sharp edges, capacitor discharge, impulse

Patterns 1-9 each capture one facet; [`patterns/10_synthesis.md`](patterns/10_synthesis.md) ties them together and ranks experiments by cost and signal strength. Level 1 (single-element) through Level 3 (three-element combinations) covers ~25 experiments total with estimated parts cost **$200-500**.

## How this feeds into HiveJournal

This repo is pinned as a git submodule inside [`hivejournal-2026`](https://github.com/jurowski/hivejournal-2026) at `vendor/energy-patent-research/`. HiveJournal's `scripts/import-energy-patents.ts` reads directly from:

- `data/patents.db` → seeds the **Patents** notebook (768 entries, one per patent)
- `patterns/*.md` → seeds the **Experiments** notebook (29 experiment entries cross-referencing their source patents)

Those notebooks power the [hivejournal.com/open-energy](https://hivejournal.com/open-energy) 10-phase pathway, the Constellation view, and the Cheer Dashboard. This repo is the upstream data pipeline; HiveJournal is the product surface.

## Contributing

New findings, additional patents, corrections, and bench-test results from the `patterns/` experiments are all welcome.

- Open an issue for discussion first on anything speculative.
- PRs should cite public sources and include reproducible steps.
- Keep the "no secrets" principle — if you can't link to a public source, it doesn't go in.

## License

[CC BY-SA 4.0](LICENSE) — share freely with attribution and under the same terms.
