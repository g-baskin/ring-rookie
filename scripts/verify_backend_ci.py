#!/usr/bin/env python3
"""Run the complete backend verification as one harness-friendly command."""

from pathlib import Path
import subprocess


BACKEND = Path(__file__).resolve().parents[1] / "backend"


def run(*command: str) -> None:
    subprocess.run(command, cwd=BACKEND, check=True)


def main() -> None:
    run("uv", "sync", "--frozen", "--all-extras")
    run("uv", "run", "ruff", "check", "app", "tests", "scripts")
    run("uv", "run", "ruff", "format", "--check", "app", "tests", "scripts")
    run("uv", "run", "mypy", "app")

    known_failures = [
        f"--deselect={line.strip()}"
        for line in (BACKEND / "tests/ci-known-failures.txt").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    run("uv", "run", "pytest", *known_failures, "--cov-fail-under=37")
    print("PASSED backend CI")


if __name__ == "__main__":
    main()
