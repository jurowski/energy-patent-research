"""
Patent data fetcher using Google Patents XHR API.

Usage:
    python3 fetch_patents.py --init --seed       # Initialize DB with seed data
    python3 fetch_patents.py --query "resonant electrolysis"
    python3 fetch_patents.py --bulk               # Run all predefined searches
    python3 fetch_patents.py --enrich             # Backfill claims/CPC/IPC/full abstract
    python3 fetch_patents.py --enrich --limit 5   # Enrich just the first 5 (dry test)
    python3 fetch_patents.py --derive             # Derive efficiency_claims/key_features
    python3 fetch_patents.py --stats              # Show database stats
"""

import argparse
import html
import json
import re
import sqlite3
import urllib.request
import urllib.parse
import urllib.error
import time
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "patents.db"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS patents (
            patent_number TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            filing_date TEXT,
            grant_date TEXT,
            inventor TEXT,
            assignee TEXT,
            ipc_codes TEXT,
            cpc_codes TEXT,
            claims_text TEXT,
            efficiency_claims TEXT,
            key_features TEXT,
            category TEXT,
            secrecy_order_suspected INTEGER DEFAULT 0,
            independently_replicated INTEGER DEFAULT 0,
            notes TEXT,
            search_query TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS citations (
            citing_patent TEXT,
            cited_patent TEXT,
            PRIMARY KEY (citing_patent, cited_patent)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            patent_number TEXT,
            tag TEXT,
            PRIMARY KEY (patent_number, tag)
        )
    """)
    conn.commit()
    return conn


def search_google_patents(query: str, num_results: int = 20, page: int = 0) -> list[dict]:
    """Search Google Patents via their XHR endpoint."""
    encoded_q = urllib.parse.quote(query)
    url = f"https://patents.google.com/xhr/query?url=q%3D{encoded_q}%26num%3D{num_results}%26page%3D{page}&exp=&tags="

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Accept": "application/json",
    })

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read())
                results = data.get("results", {})
                total = results.get("total_num_results", 0)

                patents = []
                for cluster in results.get("cluster", []):
                    for item in cluster.get("result", []):
                        p = item.get("patent", {})
                        patents.append({
                            "patent_number": p.get("publication_number", ""),
                            "title": p.get("title", "").strip(),
                            "abstract": p.get("snippet", "").replace("&hellip;", "...").strip(),
                            "filing_date": p.get("filing_date", ""),
                            "grant_date": p.get("grant_date", ""),
                            "inventor": p.get("inventor", ""),
                            "assignee": p.get("assignee", ""),
                        })

                return patents, total
        except urllib.error.HTTPError as e:
            if e.code == 503 and attempt < 2:
                wait = 10 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s (attempt {attempt+1}/3)...")
                time.sleep(wait)
                continue
            print(f"  Error querying Google Patents: {e}")
            return [], 0
        except Exception as e:
            print(f"  Error querying Google Patents: {e}")
            return [], 0
    return [], 0


def store_patents(conn: sqlite3.Connection, patents: list[dict], category: str, query: str):
    """Store fetched patents in the database."""
    c = conn.cursor()
    new_count = 0
    for p in patents:
        if not p.get("patent_number"):
            continue
        c.execute("SELECT 1 FROM patents WHERE patent_number = ?", (p["patent_number"],))
        if c.fetchone():
            continue
        c.execute("""
            INSERT INTO patents
            (patent_number, title, abstract, filing_date, grant_date,
             inventor, assignee, category, search_query, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["patent_number"], p["title"], p["abstract"],
            p["filing_date"], p["grant_date"],
            p["inventor"], p["assignee"],
            category, query,
            datetime.now().isoformat(),
        ))
        new_count += 1
    conn.commit()
    return new_count


# ─── Per-patent Enrichment ────────────────────────────────
#
# The search endpoint only returns a truncated snippet + basic metadata. The
# per-patent HTML page carries the full abstract, CPC/IPC classifications, and
# the claims text. The hivejournal importer renders all of these, so we backfill
# them here into the columns declared in init_db() but left empty by the search.


def http_get(url: str, timeout: int = 30, retries: int = 3) -> str | None:
    """Fetch a URL as text, backing off on rate limits."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 503) and attempt < retries - 1:
                wait = 10 * (attempt + 1)
                print(f"    Rate limited ({e.code}), waiting {wait}s...")
                time.sleep(wait)
                continue
            return None
        except Exception:
            if attempt < retries - 1:
                time.sleep(5)
                continue
            return None
    return None


def _parse_abstract(page: str) -> str:
    """Full abstract from the on-page section, falling back to the meta tag."""
    sec = re.search(r'<section itemprop="abstract".*?</section>', page, re.S)
    if sec:
        t = re.sub(r"<[^>]+>", " ", sec.group(0))
        t = html.unescape(t)
        t = re.sub(r"\s+", " ", t).strip()
        t = re.sub(r"^Abstract\s*", "", t)
        if len(t) > 30:
            return t
    m = re.search(r'<meta name="description" content="([^"]*)"', page)
    return html.unescape(m.group(1).strip()) if m else ""


def _parse_classifications(page: str) -> tuple[list[str], list[str]]:
    """Leaf-level CPC and IPC codes, in document order, de-duplicated.

    Each classification node renders its code in a <span itemprop="Code"> and
    marks leaves with <meta itemprop="Leaf" content="true">. CPC vs IPC is
    distinguished by the nearest preceding IsCPC flag.
    """
    cpc: list[str] = []
    ipc: list[str] = []
    for leaf in re.finditer(r'itemprop="Leaf" content="true"', page):
        window = page[max(0, leaf.start() - 400) : leaf.start()]
        codes = re.findall(r'itemprop="Code">([^<]+)</span>', window)
        if not codes:
            continue
        code = html.unescape(codes[-1]).strip()
        is_cpc = window.rfind('itemprop="IsCPC" content="true"') > window.rfind(
            'itemprop="IsCPC" content="false"'
        )
        (cpc if is_cpc else ipc).append(code)

    def dedup(seq: list[str]) -> list[str]:
        seen: list[str] = []
        for item in seq:
            if item not in seen:
                seen.append(item)
        return seen

    return dedup(cpc), dedup(ipc)


def _parse_claims(page: str) -> str:
    """Cleaned, human-readable claims text from the claims section."""
    sec = re.search(r'<section itemprop="claims".*?</section>', page, re.S)
    if not sec:
        return ""
    t = re.sub(r"</(div|p|li|section|h[1-6])>", "\n", sec.group(0))
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n[ \t]+", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    t = re.sub(r"^Claims\s*\(\s*\d+\s*\)\s*", "", t)  # drop the "Claims ( N )" header
    return t.strip()


def fetch_patent_detail(patent_number: str) -> dict | None:
    """Fetch and parse the Google Patents detail page for one patent."""
    url = f"https://patents.google.com/patent/{urllib.parse.quote(patent_number)}/en"
    page = http_get(url)
    if not page:
        return None
    cpc, ipc = _parse_classifications(page)
    return {
        "abstract": _parse_abstract(page),
        "cpc_codes": ", ".join(cpc),
        "ipc_codes": ", ".join(ipc),
        "claims_text": _parse_claims(page),
    }


def enrich_patents(conn: sqlite3.Connection, limit: int = 0, force: bool = False, delay: float = 2.0):
    """Backfill abstract/claims/CPC/IPC for patents missing that detail.

    By default only rows without claims_text are fetched (resumable); --force
    re-fetches everything. The existing abstract is only replaced when the
    detail page yields a longer one, so we never overwrite a good abstract with
    an empty foreign-patent page.
    """
    c = conn.cursor()
    if force:
        c.execute("SELECT patent_number, abstract FROM patents ORDER BY patent_number")
    else:
        c.execute(
            "SELECT patent_number, abstract FROM patents "
            "WHERE claims_text IS NULL OR TRIM(claims_text) = '' "
            "ORDER BY patent_number"
        )
    rows = c.fetchall()
    if limit > 0:
        rows = rows[:limit]

    print(f"Enriching {len(rows)} patents (force={force}, delay={delay}s)...\n")
    enriched = failed = 0
    for i, (pnum, existing_abstract) in enumerate(rows):
        detail = fetch_patent_detail(pnum)
        if detail is None:
            failed += 1
            print(f"  [{i+1}/{len(rows)}] {pnum:16s} — no page found")
        else:
            # Keep the better abstract: prefer the full one, keep old if longer.
            new_abstract = detail["abstract"]
            if not new_abstract or len(new_abstract) < len(existing_abstract or ""):
                new_abstract = existing_abstract
            c.execute(
                """
                UPDATE patents
                   SET abstract = ?, cpc_codes = ?, ipc_codes = ?,
                       claims_text = ?, updated_at = ?
                 WHERE patent_number = ?
                """,
                (
                    new_abstract,
                    detail["cpc_codes"] or None,
                    detail["ipc_codes"] or None,
                    detail["claims_text"] or None,
                    datetime.now().isoformat(),
                    pnum,
                ),
            )
            conn.commit()
            enriched += 1
            print(
                f"  [{i+1}/{len(rows)}] {pnum:16s} — "
                f"abstract:{len(new_abstract or '')} cpc:{detail['cpc_codes'].count(',')+1 if detail['cpc_codes'] else 0} "
                f"claims:{len(detail['claims_text'])}"
            )
        if i < len(rows) - 1:
            time.sleep(delay)

    print(f"\nEnrichment complete: {enriched} enriched, {failed} not found.")
    return {"enriched": enriched, "failed": failed}


# ─── Field Derivation (efficiency_claims / key_features) ──
#
# These two columns aren't on the patent page — they're what the pattern
# analysis cares about. We derive them deterministically (no API keys, fully
# reproducible) from the enriched abstract + claims: efficiency_claims collects
# sentences carrying an efficiency/energy-gain signal; key_features summarizes
# what claim 1 says the device *is* and what distinguishes it.

# Signals that mark a sentence as an efficiency / energy-performance claim.
_EFFICIENCY_SIGNALS = [
    r"\befficien\w*",
    r"\bcoefficient of performance\b", r"\bC\.?O\.?P\.?\b",
    r"\bover[\s-]?unity\b", r"\bgreater than unity\b", r"\bgreater than 100\s*%",
    r"\bexcess (?:heat|energy|power)\b", r"\banomalous (?:heat|energy)\b",
    r"\bconservation of energy\b", r"\bperpetual\b",
    r"\bfree energy\b", r"\bzero[\s-]?point\b", r"\bradiant energy\b",
    r"\benergy gain\b", r"\bself[\s-]?(?:running|sustain\w*)\b",
    r"\bout(?:put)? .{0,30}? (?:exceed|greater|more) .{0,20}?in(?:put)?\b",
    r"\bFaraday\b", r"\bhydrino\b", r"\bcold fusion\b",
    r"\bhigh(?:er|ly)?[\s-]?efficien\w*", r"\b\d{2,3}\s?%",
    r"\bkWh\b", r"\bfuel (?:gas|cell)\b",
]
_EFFICIENCY_RE = re.compile("|".join(_EFFICIENCY_SIGNALS), re.IGNORECASE)

# Where a claim stops reciting the device and starts reciting its novelty.
_DISTINGUISH_RE = re.compile(
    r"characterized (?:in that|by)|wherein|其特征在于", re.IGNORECASE
)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.;])\s+|\n+|(?<=[。；])", text)
    return [p.strip() for p in parts if p and p.strip()]


def _derive_efficiency_claims(abstract: str, claims: str) -> str:
    """Collect the sentences that actually assert an efficiency/energy claim."""
    seen: list[str] = []
    for sent in _split_sentences(f"{abstract or ''} {claims or ''}"):
        if len(sent) < 12 or len(sent) > 400:
            continue
        if _EFFICIENCY_RE.search(sent):
            norm = sent.rstrip(".;")
            if norm not in seen:
                seen.append(norm)
        if len(seen) >= 6:
            break
    return "\n".join(f"- {s}" for s in seen)


def _derive_key_features(claims: str) -> str:
    """One-line-ish summary of claim 1: what it is + what distinguishes it."""
    if not claims:
        return ""
    # Isolate claim 1 (up to the start of claim 2).
    m = re.search(r"(?:^|\n)\s*1[.。]\s*(.+?)(?=\n\s*2[.。]\s|\Z)", claims, re.S)
    claim1 = (m.group(1) if m else claims).strip()
    claim1 = re.sub(r"^Translated from Chinese\s*", "", claim1, flags=re.I).strip()

    # Preamble: what the device *is*, before it starts enumerating parts.
    preamble = re.split(
        r"\bcomprising\b|\bconsisting of\b|characterized|wherein|其特征在于|:",
        claim1, maxsplit=1, flags=re.IGNORECASE,
    )[0].strip(" ,;")

    # Distinguishing clause: the novelty the claim hangs on.
    dm = _DISTINGUISH_RE.search(claim1)
    distinguish = ""
    if dm:
        distinguish = claim1[dm.end():].strip(" ,;")
        distinguish = _split_sentences(distinguish)[0] if distinguish else ""

    parts = []
    if preamble:
        parts.append(preamble[:280])
    if distinguish:
        parts.append(f"Distinguished by: {distinguish[:280]}")
    return "\n\n".join(parts)


def derive_patents(conn: sqlite3.Connection, force: bool = False):
    """Fill efficiency_claims and key_features from enriched abstract + claims."""
    c = conn.cursor()
    if force:
        c.execute("SELECT patent_number, abstract, claims_text FROM patents")
    else:
        c.execute(
            "SELECT patent_number, abstract, claims_text FROM patents "
            "WHERE (efficiency_claims IS NULL OR TRIM(efficiency_claims) = '') "
            "   OR (key_features IS NULL OR TRIM(key_features) = '')"
        )
    rows = c.fetchall()
    print(f"Deriving efficiency_claims / key_features for {len(rows)} patents...")

    eff_filled = feat_filled = 0
    for pnum, abstract, claims in rows:
        eff = _derive_efficiency_claims(abstract or "", claims or "")
        feat = _derive_key_features(claims or "")
        if eff:
            eff_filled += 1
        if feat:
            feat_filled += 1
        c.execute(
            "UPDATE patents SET efficiency_claims = ?, key_features = ?, updated_at = ? "
            "WHERE patent_number = ?",
            (eff or None, feat or None, datetime.now().isoformat(), pnum),
        )
    conn.commit()
    print(
        f"Done: efficiency_claims filled for {eff_filled}, "
        f"key_features for {feat_filled} of {len(rows)}."
    )
    return {"efficiency": eff_filled, "features": feat_filled}


def add_patent_manually(conn: sqlite3.Connection, patent_data: dict):
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO patents
        (patent_number, title, abstract, filing_date, grant_date,
         inventor, assignee, ipc_codes, category, notes, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patent_data.get("patent_number"),
        patent_data.get("title"),
        patent_data.get("abstract"),
        patent_data.get("filing_date"),
        patent_data.get("grant_date"),
        patent_data.get("inventor"),
        patent_data.get("assignee"),
        patent_data.get("ipc_codes"),
        patent_data.get("category"),
        patent_data.get("notes"),
        datetime.now().isoformat(),
    ))
    conn.commit()


# Bulk search queries organized by category
BULK_SEARCHES = [
    # Electromagnetic - resonance & coil geometry
    ("electromagnetic", "bifilar coil energy generator"),
    ("electromagnetic", "magnetic flux switching energy conversion"),
    ("electromagnetic", "permanent magnet motor high efficiency over-unity"),
    ("electromagnetic", "pulsed DC motor back EMF energy recovery"),
    ("electromagnetic", "toroidal coil zero point energy"),
    ("electromagnetic", "radiant energy electrical generator"),
    ("electromagnetic", "self-running magnetic motor generator"),
    ("electromagnetic", "asymmetric magnetic field energy"),

    # Electrochemical - water splitting & anomalous efficiency
    ("electrochemical", "resonant electrolysis water fuel cell"),
    ("electrochemical", "water electrolysis high efficiency pulsed"),
    ("electrochemical", "Brown's gas HHO generator efficient"),
    ("electrochemical", "electrolysis overunity anomalous heat"),
    ("electrochemical", "cavitation water dissociation energy"),

    # LENR / Cold Fusion
    ("lenr", "low energy nuclear reaction palladium deuterium"),
    ("lenr", "cold fusion excess heat electrolysis"),
    ("lenr", "lattice assisted nuclear reaction"),
    ("lenr", "nickel hydrogen exothermic reaction"),

    # Plasma & discharge
    ("plasma", "pulsed abnormal glow discharge energy"),
    ("plasma", "plasma electrolysis excess energy"),
    ("plasma", "high voltage discharge free energy"),
    ("plasma", "vacuum energy extraction device"),

    # Solid state
    ("solid-state", "solid state energy converter thermionic"),
    ("solid-state", "Casimir effect energy harvesting"),
    ("solid-state", "piezoelectric ambient energy harvester high efficiency"),
    ("solid-state", "quantum vacuum energy extraction"),

    # Thermodynamic
    ("thermodynamic", "heat pump COP greater than Carnot"),
    ("thermodynamic", "waste heat recovery high efficiency thermoelectric"),
    ("thermodynamic", "vortex tube energy separation anomalous"),

    # Key inventors
    ("electromagnetic", "inventor:\"Nikola Tesla\" energy"),
    ("electromagnetic", "inventor:\"Edwin Gray\" motor"),
    ("electrochemical", "inventor:\"Stanley Meyer\" fuel"),
    ("electromagnetic", "inventor:\"John Bedini\" motor battery"),
    ("lenr", "inventor:\"Andrea Rossi\" energy reactor"),
    ("lenr", "inventor:\"Randell Mills\" hydrino energy"),
]

SEED_PATENTS = [
    {
        "patent_number": "US4936961",
        "title": "Method for the production of a fuel gas",
        "inventor": "Stanley A. Meyer",
        "category": "electrochemical",
        "notes": "Water fuel cell. Claims resonant electrolysis at far less energy than Faraday minimum.",
    },
    {
        "patent_number": "US3890548",
        "title": "Pulsed capacitor discharge electric engine",
        "inventor": "Edwin V. Gray",
        "category": "electromagnetic",
        "notes": "EMA motor. Claims recovery of energy from back-EMF via cold electricity.",
    },
    {
        "patent_number": "US4595975",
        "title": "Efficient power supply suitable for inductive loads",
        "inventor": "Edwin V. Gray",
        "category": "electromagnetic",
        "notes": "Second Gray patent. Capacitor discharge power supply.",
    },
    {
        "patent_number": "US5449989",
        "title": "Energy conversion system",
        "inventor": "Paulo N. Correa, Alexandra N. Correa",
        "category": "plasma",
        "notes": "PAGD (Pulsed Abnormal Glow Discharge) reactor.",
    },
    {
        "patent_number": "US512340",
        "title": "Coil for electro-magnets",
        "inventor": "Nikola Tesla",
        "category": "electromagnetic",
        "notes": "Bifilar coil patent. Foundational geometry used in many later devices.",
    },
    {
        "patent_number": "US685957",
        "title": "Apparatus for the utilization of radiant energy",
        "inventor": "Nikola Tesla",
        "category": "electromagnetic",
        "notes": "Tesla radiant energy patent.",
    },
    {
        "patent_number": "US787412",
        "title": "Art of transmitting electrical energy through the natural mediums",
        "inventor": "Nikola Tesla",
        "category": "electromagnetic",
        "notes": "Wireless power transmission through earth/atmosphere.",
    },
]


def print_stats(conn: sqlite3.Connection):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM patents")
    total = c.fetchone()[0]
    print(f"\nTotal patents in database: {total}")

    c.execute("SELECT category, COUNT(*) FROM patents GROUP BY category ORDER BY COUNT(*) DESC")
    print("\nBy category:")
    for row in c.fetchall():
        print(f"  {row[0] or 'uncategorized':25s} {row[1]:4d}")

    c.execute("SELECT search_query, COUNT(*) FROM patents WHERE search_query IS NOT NULL GROUP BY search_query ORDER BY COUNT(*) DESC LIMIT 15")
    print("\nTop queries:")
    for row in c.fetchall():
        print(f"  {row[0]:55s} {row[1]:4d}")

    # Show some sample titles
    c.execute("SELECT patent_number, title, inventor, category FROM patents ORDER BY RANDOM() LIMIT 10")
    print("\nSample patents:")
    for row in c.fetchall():
        inv = row[2] or "Unknown"
        print(f"  {row[0]:20s} | {row[1][:50]:50s} | {inv[:25]:25s} | {row[3] or '?'}")


def main():
    parser = argparse.ArgumentParser(description="Fetch and catalog patent data")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--category", "-c", default="uncategorized", help="Category for query results")
    parser.add_argument("--bulk", action="store_true", help="Run all predefined bulk searches")
    parser.add_argument("--seed", action="store_true", help="Populate DB with seed patents")
    parser.add_argument("--init", action="store_true", help="Initialize the database")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--num", "-n", type=int, default=20, help="Results per query (default 20)")
    parser.add_argument("--enrich", action="store_true",
                        help="Backfill abstract/claims/CPC/IPC from per-patent pages")
    parser.add_argument("--force", action="store_true",
                        help="With --enrich, re-fetch all patents (not just those missing claims)")
    parser.add_argument("--limit", type=int, default=0,
                        help="With --enrich, cap the number of patents fetched (0 = no cap)")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="With --enrich, seconds to wait between patent fetches (default 2)")
    parser.add_argument("--derive", action="store_true",
                        help="Derive efficiency_claims/key_features from enriched abstract+claims")
    args = parser.parse_args()

    conn = init_db()

    if args.init:
        print(f"Database initialized at {DB_PATH}")

    if args.seed:
        for patent in SEED_PATENTS:
            add_patent_manually(conn, patent)
            print(f"  Seeded: {patent['patent_number']} — {patent['title']}")
        print(f"Seeded {len(SEED_PATENTS)} patents.")

    if args.stats:
        print_stats(conn)
        conn.close()
        return

    if args.enrich:
        enrich_patents(conn, limit=args.limit, force=args.force, delay=args.delay)
        conn.close()
        return

    if args.derive:
        derive_patents(conn, force=args.force)
        conn.close()
        return

    if args.query:
        print(f"Searching: {args.query}")
        patents, total = search_google_patents(args.query, args.num)
        print(f"  Found {total} total results, fetched {len(patents)}")
        new = store_patents(conn, patents, args.category, args.query)
        print(f"  Stored {new} new patents")
        for p in patents[:5]:
            print(f"    {p['patent_number']:20s} {p['title'][:60]}")

    if args.bulk:
        print(f"Running {len(BULK_SEARCHES)} bulk searches...\n")
        total_new = 0
        for i, (category, query) in enumerate(BULK_SEARCHES):
            print(f"[{i+1}/{len(BULK_SEARCHES)}] ({category}) {query}")
            patents, total = search_google_patents(query, args.num)
            new = store_patents(conn, patents, category, query)
            total_new += new
            print(f"  → {total} results, {len(patents)} fetched, {new} new stored")

            # Be polite to Google — longer delay to avoid rate limiting
            if i < len(BULK_SEARCHES) - 1:
                time.sleep(5)

        print(f"\n{'='*60}")
        print(f"Bulk search complete. {total_new} new patents added.")
        print_stats(conn)

    if args.init and not args.seed and not args.query and not args.bulk:
        print("Database ready. Use --seed, --query, or --bulk to populate.")

    conn.close()


if __name__ == "__main__":
    main()
