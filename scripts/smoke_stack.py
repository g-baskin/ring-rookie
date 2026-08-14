#!/usr/bin/env python3
"""Bounded smoke test for the persistent local development stack."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Check:
    name: str
    probe: Callable[[], None]


def run_compose(*args: str) -> str:
    result = subprocess.run(
        ["docker", "compose", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def require_service_health(service: str) -> None:
    container_id = run_compose("ps", "-q", service)
    if not container_id:
        raise RuntimeError(f"{service} has no running container")

    health = subprocess.run(
        [
            "docker",
            "inspect",
            "--format",
            "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}",
            container_id,
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if health != "healthy":
        raise RuntimeError(f"{service} is {health}")


def require_http(url: str, expected_status: int = 200) -> None:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.status
            response.read()
    except urllib.error.HTTPError as error:
        status = error.code

    if status != expected_status:
        raise RuntimeError(f"{url} returned HTTP {status}")


def require_json_status(url: str) -> None:
    with urllib.request.urlopen(url, timeout=5) as response:
        payload = json.load(response)
    if response.status != 200 or payload.get("status") != "healthy":
        raise RuntimeError(f"{url} is not healthy")


def wait_for(checks: list[Check], timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    pending = {check.name: check for check in checks}
    errors: dict[str, str] = {}

    while pending and time.monotonic() < deadline:
        for name, check in list(pending.items()):
            try:
                check.probe()
            except Exception as error:  # Smoke output needs the final probe failure.
                errors[name] = str(error)
            else:
                print(f"PASS {name}")
                del pending[name]
                errors.pop(name, None)
        if pending:
            time.sleep(2)

    if pending:
        for name in pending:
            print(f"FAIL {name}: {errors.get(name, 'timed out')}", file=sys.stderr)
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    checks = [
        Check("PostgreSQL health", lambda: require_service_health("postgres")),
        Check("Redis health", lambda: require_service_health("redis")),
        Check(
            "backend readiness",
            lambda: require_json_status("http://localhost:8000/health/ready"),
        ),
        Check("frontend login", lambda: require_http("http://localhost:4173/login")),
        Check(
            "frontend API proxy",
            lambda: require_json_status("http://localhost:4173/health/ready"),
        ),
    ]
    wait_for(checks, args.timeout)
    print("Stack smoke test passed.")


if __name__ == "__main__":
    main()
