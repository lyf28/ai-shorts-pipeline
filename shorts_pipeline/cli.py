from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from shorts_pipeline.config import Settings
from shorts_pipeline.pipeline import Pipeline


def main() -> int:
    # Windows terminals may otherwise use a legacy code page that cannot print a Unicode workspace path.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="Generate a 20–30 second vertical AI short locally.")
    parser.add_argument("--topic", help="Optional seed topic for the creative idea")
    parser.add_argument("--dry-run", action="store_true", help="Generate and persist idea/script/storyboard, but do not create media")
    parser.add_argument("--verbose", action="store_true", help="Enable diagnostic logs")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        output = Pipeline(Settings.from_root(Path(__file__).resolve().parents[1])).run(args.topic, args.dry_run)
    except Exception as error:
        logging.getLogger(__name__).error("Pipeline failed: %s", error)
        return 1
    print("Dry run completed; storyboard is saved in data/pipeline.sqlite3." if output is None else f"Video created: {output}")
    return 0
