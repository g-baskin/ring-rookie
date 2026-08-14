#!/usr/bin/env python3
"""Run the complete frontend verification as one harness-friendly command."""

from pathlib import Path
import subprocess


FRONTEND = Path(__file__).resolve().parents[1] / "frontend"


def run(*command: str) -> None:
    subprocess.run(command, cwd=FRONTEND, check=True)


def main() -> None:
    run("npm", "run", "check")
    run("npm", "test")
    run("npm", "run", "build")
    print("PASSED frontend CI and production build")


if __name__ == "__main__":
    main()
