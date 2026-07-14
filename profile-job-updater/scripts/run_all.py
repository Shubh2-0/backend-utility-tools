"""Orchestrator: runs all portal updaters. Skips those with missing creds."""
from __future__ import annotations

import asyncio
import logging
import os
import random
import sys
from datetime import datetime

from dotenv import load_dotenv

from . import foundit, indeed, naukri, shine, timesjobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("updater.main")

PORTALS = [
    ("Naukri", naukri.update),
    ("Shine", shine.update),
    ("Foundit", foundit.update),
    ("TimesJobs", timesjobs.update),
    ("Indeed", indeed.update),
]


async def main() -> int:
    load_dotenv()
    log.info("=== Profile Update Run @ %s ===", datetime.now().isoformat(timespec="seconds"))

    # Shuffle so portals aren't always hit in the same order (less pattern-y)
    portals = PORTALS.copy()
    random.shuffle(portals)

    results: dict[str, str] = {}
    for name, fn in portals:
        try:
            # Jitter between portals so it doesn't look automated
            await asyncio.sleep(random.uniform(15, 45))
            ok = await fn()
            results[name] = "OK" if ok else "SKIP/FAIL"
        except Exception as e:
            log.exception("%s crashed: %s", name, e)
            results[name] = f"ERROR: {e.__class__.__name__}"

    log.info("=== Summary ===")
    for name, status in results.items():
        log.info("  %-12s %s", name, status)

    # Exit non-zero only if EVERY portal with creds failed
    had_any_ok = any(v == "OK" for v in results.values())
    had_any_creds = any(os.getenv(f"{p.upper()}_EMAIL") for p, _ in PORTALS)
    if had_any_creds and not had_any_ok:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
