#!/usr/bin/env python3
"""Run Alembic drift detection and reject changes outside the reviewed baseline."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "backend" / "migrations" / "schema-drift-baseline.sha256"


def normalize_output(output: str) -> str:
    output = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", output)
    relevant = [
        line.strip()
        for line in output.splitlines()
        if "New upgrade operations detected:" in line
    ]
    return "\n".join(relevant)


def digest(output: str) -> str:
    return hashlib.sha256(normalize_output(output).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args()

    result = subprocess.run(
        ["uv", "run", "alembic", "check"],
        cwd=ROOT / "backend",
        capture_output=True,
        text=True,
        check=False,
    )
    output = f"{result.stdout}\n{result.stderr}"

    if result.returncode == 0:
        print("alembic: no schema drift")
        return 0

    normalized = normalize_output(output)
    if not normalized:
        print("alembic check failed without a schema-drift report", file=sys.stderr)
        print(output, file=sys.stderr)
        return 1

    current_digest = digest(output)
    if args.write_baseline:
        args.baseline.write_text(f"{current_digest}\n")
        print(f"wrote schema drift baseline {current_digest}")
        return 0

    expected_digest = args.baseline.read_text().strip()
    if current_digest != expected_digest:
        print(
            "alembic: schema drift changed from the reviewed baseline", file=sys.stderr
        )
        print(f"expected {expected_digest}", file=sys.stderr)
        print(f"current  {current_digest}", file=sys.stderr)
        return 1

    print("alembic: known schema drift unchanged; baseline cleanup remains required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
