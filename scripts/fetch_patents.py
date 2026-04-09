"""
Patent data fetcher using Google Patents and USPTO APIs.

Usage:
    python fetch_patents.py --query "energy conversion high efficiency"
    python fetch_patents.py --inventor "Stanley Meyer"
    python fetch_patents.py --patent-number "US4936961"
"""

import argparse
import json
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "patents.db"


def init_db():
    """Initialize the SQLite database with our schema."""
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


def search_google_patents(query: str, num_results: int = 20) -> list[dict]:
    """
    Search Google Patents via their public interface.
    Note: Google Patents doesn't have an official API, so this uses
    the SerpAPI or similar service. For a free alternative, we can
    scrape the public search page or use USPTO's PatentsView API.
    """
    # USPTO PatentsView API (free, no key required)
    base_url = "https://api.patentsview.org/patents/query"
    payload = {
        "q": {"_text_any": {"patent_abstract": query}},
        "f": [
            "patent_number",
            "patent_title",
            "patent_abstract",
            "patent_date",
            "inventor_last_name",
            "inventor_first_name",
            "assignee_organization",
        ],
        "o": {"per_page": num_results},
    }

    req = urllib.request.Request(
        base_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return data.get("patents", [])
    except Exception as e:
        print(f"Error querying PatentsView API: {e}")
        return []


def add_patent_manually(conn: sqlite3.Connection, patent_data: dict):
    """Add a patent record manually to the database."""
    c = conn.cursor()
    c.execute(
        """
        INSERT OR REPLACE INTO patents
        (patent_number, title, abstract, filing_date, grant_date,
         inventor, assignee, ipc_codes, category, notes, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
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
        ),
    )
    conn.commit()


# Seed patents — key devices from our research list
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


def main():
    parser = argparse.ArgumentParser(description="Fetch and catalog patent data")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--inventor", "-i", help="Search by inventor name")
    parser.add_argument("--patent-number", "-p", help="Fetch specific patent")
    parser.add_argument(
        "--seed", action="store_true", help="Populate DB with seed patents"
    )
    parser.add_argument(
        "--init", action="store_true", help="Initialize the database"
    )
    args = parser.parse_args()

    if args.init or args.seed:
        conn = init_db()
        print(f"Database initialized at {DB_PATH}")

        if args.seed:
            for patent in SEED_PATENTS:
                add_patent_manually(conn, patent)
                print(f"  Added: {patent['patent_number']} — {patent['title']}")
            print(f"\nSeeded {len(SEED_PATENTS)} patents.")

        conn.close()
        return

    if args.query:
        results = search_google_patents(args.query)
        for r in results:
            print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
