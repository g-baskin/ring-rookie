import json
from pathlib import Path

from scripts.check_dependency_audit import npm_advisories, python_advisories


def test_python_advisories_extracts_unique_ids() -> None:
    report = {
        "dependencies": [
            {"vulns": [{"id": "GHSA-one"}, {"id": "GHSA-two"}]},
            {"vulns": [{"id": "GHSA-one"}]},
        ]
    }

    assert python_advisories(report) == {"GHSA-one", "GHSA-two"}


def test_npm_advisories_uses_stable_ghsa_id() -> None:
    report = {
        "vulnerabilities": {
            "package": {
                "via": [
                    {"url": "https://github.com/advisories/GHSA-one"},
                    "transitive-package",
                ]
            }
        }
    }

    assert npm_advisories(report) == {"GHSA-one"}


def test_cli_rejects_new_advisory(tmp_path: Path, monkeypatch) -> None:
    from scripts import check_dependency_audit

    baseline = tmp_path / "baseline.json"
    python_report = tmp_path / "python.json"
    npm_report = tmp_path / "npm.json"
    baseline.write_text(json.dumps({"python": [], "npm": []}))
    python_report.write_text(
        json.dumps({"dependencies": [{"vulns": [{"id": "GHSA-new"}]}]})
    )
    npm_report.write_text(json.dumps({"vulnerabilities": {}}))
    monkeypatch.setattr(
        "sys.argv",
        [
            "check_dependency_audit.py",
            "--baseline",
            str(baseline),
            "--python-report",
            str(python_report),
            "--npm-report",
            str(npm_report),
        ],
    )

    assert check_dependency_audit.main() == 1
