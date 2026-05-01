"""Re-classify existing raw.jsonl with the refined judge prompt.

Reads results/raw.jsonl, replaces the judge fields on each record, writes back
in place. Skips records where the model call itself failed (no content to judge).
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from runner import judge_response, GLOBAL_CONCURRENCY  # noqa: E402

load_dotenv(Path(__file__).parent.parent / ".env")

RAW = Path(__file__).parent.parent / "results" / "raw.jsonl"


async def rejudge_one(record, sem):
    if not record.get("ok"):
        # Keep the existing error category — call genuinely failed
        return record
    async with sem:
        j = await judge_response(record.get("content", "") or "")
    record.update(j)
    return record


async def main():
    rows = [json.loads(l) for l in RAW.open() if l.strip()]
    sem = asyncio.Semaphore(GLOBAL_CONCURRENCY)
    print(f"Re-judging {len(rows)} records...")
    out = await asyncio.gather(*[rejudge_one(r, sem) for r in rows])
    with RAW.open("w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    judge_cost = sum((r.get("judge_cost_usd") or 0.0) for r in out)
    print(f"Done. Judge cost: ${judge_cost:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
