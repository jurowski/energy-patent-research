"""
Enrich the patent corpus so downstream analysis has something to read.

Right now patents.db is ~70K tokens of thin metadata: title + a one-sentence
snippet + dates + codes. `claims_text`, `efficiency_claims`, and `key_features`
are empty for all 768 rows. This script fills them in two independent stages:

  Stage A  (--fetch)    raw full text  →  claims_text
                        Best-effort scrape of the Google Patents page. No key.
                        Legitimately fails for pre-1976 patents with no OCR'd
                        full text (Tesla et al.) — those stay null, recorded.

  Stage B  (--extract)  claims_text  →  efficiency_claims + key_features
                        A Claude pass that *reads* the claims and pulls out the
                        interpretive fields. Structured output, so the result is
                        guaranteed-valid JSON. Falls back to title+abstract when
                        claims_text is missing (lower confidence, flagged).

Run Stage A, then Stage B:
    python3 enrich_patents.py --fetch                 # scrape claims (slow, polite)
    python3 enrich_patents.py --extract               # Claude extraction pass
    python3 enrich_patents.py --extract --limit 15    # cheap trial on 15 rows first

Auth: the Anthropic SDK resolves credentials from ANTHROPIC_API_KEY or an
`ant auth login` profile — nothing to hardcode. Requires `pip install anthropic`.
"""

import argparse
import json
import re
import sqlite3
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "patents.db"

MODEL = "claude-opus-4-8"  # swap to "claude-fable-5" if you want the frontier here
FETCH_DELAY_S = 2.0        # be polite to Google Patents

# ─── Stage A: raw full-text scrape (the swappable, fragile part) ──────────────

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _strip_html(html: str) -> str:
    return _WS_RE.sub(" ", _TAG_RE.sub(" ", html)).strip()


def fetch_full_text(patent_number: str) -> dict:
    """
    Best-effort fetch of full claims + abstract from the public Google Patents
    page. Returns {"claims_text": str|None, "full_abstract": str|None, "status": str}.

    This is the deliberately-isolated brittle bit. If Google changes their markup
    or you want a sturdier source (USPTO PatentsView, EPO OPS, Lens.org — most
    need a free API key), replace ONLY this function; the rest of the pipeline is
    agnostic to where the text came from.
    """
    num = patent_number.strip().replace(" ", "").replace("-", "")
    url = f"https://patents.google.com/patent/{num}/en"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return {"claims_text": None, "full_abstract": None, "status": f"http_{e.code}"}
    except Exception as e:  # noqa: BLE001 — network is the boundary; record and move on
        return {"claims_text": None, "full_abstract": None, "status": f"err_{type(e).__name__}"}

    # Abstract: Google embeds it in <meta name="description">
    abs = re.search(r'<meta name="description" content="([^"]+)"', html)
    full_abstract = abs.group(1).strip() if abs else None

    # Claims: the claims section carries itemprop="claims"
    claims_block = re.search(
        r'itemprop="claims".*?>(.*?)</section>', html, re.DOTALL | re.IGNORECASE
    )
    claims_text = _strip_html(claims_block.group(1)) if claims_block else None
    if claims_text and len(claims_text) < 40:  # empty scaffold, not real claims
        claims_text = None

    status = "ok" if claims_text else ("abstract_only" if full_abstract else "empty")
    return {"claims_text": claims_text, "full_abstract": full_abstract, "status": status}


def run_fetch(conn: sqlite3.Connection, limit: int | None) -> None:
    c = conn.cursor()
    q = "SELECT patent_number FROM patents WHERE claims_text IS NULL OR claims_text = ''"
    if limit:
        q += f" LIMIT {int(limit)}"
    rows = [r[0] for r in c.execute(q).fetchall()]
    print(f"Stage A: fetching full text for {len(rows)} patents...\n")

    stats = {"ok": 0, "abstract_only": 0, "empty": 0, "err": 0}
    for i, pn in enumerate(rows, 1):
        res = fetch_full_text(pn)
        conn.execute(
            "UPDATE patents SET claims_text = ?, "
            "abstract = COALESCE(NULLIF(?, ''), abstract), "
            "updated_at = CURRENT_TIMESTAMP WHERE patent_number = ?",
            (res["claims_text"], res["full_abstract"] or "", pn),
        )
        conn.commit()
        bucket = res["status"] if res["status"] in stats else "err"
        stats[bucket] = stats.get(bucket, 0) + 1
        print(f"  [{i}/{len(rows)}] {pn:18s} {res['status']}")
        if i < len(rows):
            time.sleep(FETCH_DELAY_S)

    print(f"\nStage A done: {stats}")


# ─── Stage B: Claude reads the claims and pulls structured fields ─────────────

EXTRACT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "has_efficiency_claim": {
            "type": "boolean",
            "description": "True if the patent claims high/anomalous efficiency, "
            "excess energy, over-unity, COP>1, or excess heat.",
        },
        "efficiency_claims": {
            "type": "string",
            "description": "The specific efficiency/energy claim in the patent's own "
            "framing, one or two sentences. Empty string if none.",
        },
        "key_features": {
            "type": "string",
            "description": "The core technical mechanism: materials, geometry, "
            "waveform, frequency, topology. 2-4 sentences, grounded in the text.",
        },
    },
    "required": ["has_efficiency_claim", "efficiency_claims", "key_features"],
}

EXTRACT_SYSTEM = (
    "You extract structured technical facts from a single energy-device patent. "
    "Ground every field in the supplied text — do not infer claims that aren't "
    "stated. If the source is only a title and short abstract, extract what you "
    "can and keep key_features conservative."
)


def _fable_kwargs(model: str) -> dict:
    # Fable refusals are opt-in to recover from; wire a fallback by default.
    if model.startswith("claude-fable") or model.startswith("claude-mythos"):
        return {"betas": ["server-side-fallback-2026-06-01"],
                "fallbacks": [{"model": "claude-opus-4-8"}]}
    return {}


def _extract_params(patent: dict, model: str) -> dict:
    """The messages.create kwargs for one patent — shared by threaded + batch paths."""
    source = patent.get("claims_text") or (
        f"TITLE: {patent.get('title', '')}\nABSTRACT: {patent.get('abstract', '')}"
    )
    return {
        "model": model,
        "max_tokens": 1500,
        "system": EXTRACT_SYSTEM,
        "output_config": {"effort": "low",
                          "format": {"type": "json_schema", "schema": EXTRACT_SCHEMA}},
        "messages": [{"role": "user",
                      "content": f"Patent {patent['patent_number']}:\n\n{source[:24000]}"}],
    }


def _parse_json_message(msg) -> dict:
    # structured outputs guarantees valid JSON matching the schema
    return json.loads(next((b.text for b in msg.content if b.type == "text"), "{}"))


def extract_one(client, model: str, patent: dict) -> dict:
    params = _extract_params(patent, model)
    fable = _fable_kwargs(model)
    create = client.beta.messages.create if fable else client.messages.create
    return _parse_json_message(create(**params, **fable))


def _apply_extract(conn, pn, out) -> None:
    conn.execute(
        "UPDATE patents SET efficiency_claims = ?, key_features = ?, "
        "updated_at = CURRENT_TIMESTAMP WHERE patent_number = ?",
        (out["efficiency_claims"], out["key_features"], pn),
    )
    conn.commit()


def run_extract(conn: sqlite3.Connection, model: str, limit: int | None,
                concurrency: int, use_batch: bool) -> None:
    from anthropic import Anthropic

    client = Anthropic()
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    q = ("SELECT patent_number, title, abstract, claims_text FROM patents "
         "WHERE key_features IS NULL OR key_features = ''")
    if limit:
        q += f" LIMIT {int(limit)}"
    rows = [dict(r) for r in c.execute(q).fetchall()]
    print(f"Stage B: extracting structured fields for {len(rows)} patents ({model})...\n")

    if use_batch:
        # 50% cheaper, async (<~1h). Note: server-side refusal fallbacks are
        # rejected on the Batches API, so _extract_params carries none by design.
        if _fable_kwargs(model):
            print("  (batch + Fable: no server-side fallbacks — refusals surface as null results)")
        from anthropic_batch import submit_and_collect

        idmap = {f"p{i}": p for i, p in enumerate(rows)}
        reqs = [{"custom_id": cid, "params": _extract_params(p, model)}
                for cid, p in idmap.items()]
        results = submit_and_collect(client, reqs, label="extract")
        done = 0
        for cid, msg in results.items():
            pn = idmap[cid]["patent_number"]
            if msg is None:
                print(f"  {pn:18s} no result (errored/expired)")
                continue
            _apply_extract(conn, pn, _parse_json_message(msg))
            done += 1
        print(f"\nStage B (batch) done: {done}/{len(rows)} enriched.")
        return

    def work(p):
        try:
            return p["patent_number"], extract_one(client, model, p)
        except Exception as e:  # noqa: BLE001
            return p["patent_number"], {"_error": str(e)}

    done = 0
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        for pn, out in ((f.result()) for f in as_completed(pool.submit(work, p) for p in rows)):
            done += 1
            if "_error" in out:
                print(f"  [{done}/{len(rows)}] {pn:18s} ERROR {out['_error'][:60]}")
                continue
            _apply_extract(conn, pn, out)
            flag = "⚡" if out["has_efficiency_claim"] else "  "
            print(f"  [{done}/{len(rows)}] {pn:18s} {flag} {out['key_features'][:60]}")

    print(f"\nStage B done: {done} patents enriched.")


def main():
    ap = argparse.ArgumentParser(description="Enrich patent corpus (claims + extracted fields)")
    ap.add_argument("--fetch", action="store_true", help="Stage A: scrape claims_text")
    ap.add_argument("--extract", action="store_true", help="Stage B: Claude structured extraction")
    ap.add_argument("--limit", type=int, help="Only process N rows (trial runs)")
    ap.add_argument("--model", default=MODEL, help="Claude model for Stage B")
    ap.add_argument("--concurrency", type=int, default=8, help="Parallel Claude calls in Stage B")
    ap.add_argument("--batch", action="store_true",
                    help="Stage B via Message Batches API (50%% cheaper, async, <~1h)")
    args = ap.parse_args()

    if not (args.fetch or args.extract):
        ap.error("pick at least one of --fetch / --extract")

    conn = sqlite3.connect(DB_PATH)
    if args.fetch:
        run_fetch(conn, args.limit)
    if args.extract:
        run_extract(conn, args.model, args.limit, args.concurrency, args.batch)
    conn.close()


if __name__ == "__main__":
    main()
