#!/usr/bin/env python3
"""Fail when dependency audits report advisories outside the reviewed baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "security/dependency-audit-baseline.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def python_advisories(report: dict[str, Any]) -> set[str]:
    return {
        vulnerability["id"]
        for dependency in report.get("dependencies", [])
        for vulnerability in dependency.get("vulns", [])
    }


def npm_advisories(report: dict[str, Any]) -> set[str]:
    advisories: set[str] = set()
    for dependency in report.get("vulnerabilities", {}).values():
        for vulnerability in dependency.get("via", []):
            if not isinstance(vulnerability, dict):
                continue
            url = vulnerability.get("url", "")
            if url:
                advisories.add(url.rsplit("/", 1)[-1])
    return advisories


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python-report", type=Path, required=True)
    parser.add_argument("--npm-report", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    args = parser.parse_args()

    baseline = load_json(args.baseline)
    current = {
        "python": python_advisories(load_json(args.python_report)),
        "npm": npm_advisories(load_json(args.npm_report)),
    }

    has_new_findings = False
    for ecosystem, advisory_ids in current.items():
        reviewed = set(baseline.get(ecosystem, []))
        new_findings = sorted(advisory_ids - reviewed)
        resolved_findings = sorted(reviewed - advisory_ids)
        print(
            f"{ecosystem}: {len(advisory_ids)} active, "
            f"{len(new_findings)} new, {len(resolved_findings)} resolved"
        )
        for advisory_id in new_findings:
            print(f"{ecosystem}: new advisory {advisory_id}")
        if resolved_findings:
            print(f"{ecosystem}: baseline cleanup available")
        has_new_findings |= bool(new_findings)

    return int(has_new_findings)


if __name__ == "__main__":
    sys.exit(main())
