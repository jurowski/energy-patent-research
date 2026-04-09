"""
Patent data fetcher using Google Patents XHR API.

Usage:
    python3 fetch_patents.py --init --seed       # Initialize DB with seed data
    python3 fetch_patents.py --query "resonant electrolysis"
    python3 fetch_patents.py --bulk               # Run all predefined searches
    python3 fetch_patents.py --stats              # Show database stats
"""

import argparse
import json
import sqlite3
import urllib.request
import urllib.parse
import urllib.error
import time
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "patents.db"


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
