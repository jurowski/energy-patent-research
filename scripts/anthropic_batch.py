"""
Message Batches helper shared by enrich_patents.py and semantic_clusters.py.

The Batches API runs Messages requests asynchronously at 50% of standard price.
Right size for re-enriching a corpus: not latency-sensitive, hundreds of small
independent calls. Trade-off vs. the threaded path: cheaper, higher throughput,
but you wait (usually <1h) and you can't stream.

Two caveats baked in below:
  - Results come back UNORDERED — always key by custom_id, never by position.
  - Server-side refusal `fallbacks` are rejected on the Batches API, so a Fable
    batch runs without them; handle a refusal result yourself if you go that route.
"""

import time


def submit_and_collect(client, requests, poll_s=30, label="batch"):
    """
    requests: list of {"custom_id": str, "params": {<messages.create kwargs>}}
    returns:  {custom_id: message | None}   (None = errored / expired / canceled)
    """
    batch = client.messages.batches.create(requests=requests)
    print(f"  {label}: submitted {len(requests)} requests as {batch.id}")

    while True:
        b = client.messages.batches.retrieve(batch.id)
        if b.processing_status == "ended":
            break
        counts = b.request_counts
        print(f"  {label}: {b.processing_status} "
              f"(processing={counts.processing} succeeded={counts.succeeded} "
              f"errored={counts.errored})")
        time.sleep(poll_s)

    out, ok, bad = {}, 0, 0
    for result in client.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            out[result.custom_id] = result.result.message
            ok += 1
        else:
            out[result.custom_id] = None
            bad += 1
    print(f"  {label}: done — {ok} succeeded, {bad} not")
    return out
