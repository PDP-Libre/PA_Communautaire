# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import typer

from .. import utils
from ..lib.conf import DEFAULT_BRANCH, DEFAULT_REPO
from ..lib.process import install_run
from ..lib.settings import settings

app = typer.Typer()


def parse_junit_xml(xml_path: Path) -> tuple[int, int]:
    """Parse JUnit XML report to extract test counts.

    Args:
        xml_path: Path to the JUnit XML report

    Returns:
        Tuple of (passed_count, failed_count)
    """
    if not xml_path.exists():
        return 0, 0

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # JUnit XML has testsuite element with tests, failures, errors attributes
    total_tests = 0
    total_failures = 0
    total_errors = 0

    for testsuite in root.iter("testsuite"):
        total_tests += int(testsuite.get("tests", 0))
        total_failures += int(testsuite.get("failures", 0))
        total_errors += int(testsuite.get("errors", 0))

    passed = total_tests - total_failures - total_errors
    failed = total_failures + total_errors
    return passed, failed


def run_tests(
    package_name: str, package_path: Path, report_dir: Path
) -> tuple[int, int, int]:
    """Run pytest for a package and generate reports.

    Args:
        package_name: Name of the package (for display)
        package_path: Path to the package directory
        report_dir: Path to the report output directory

    Returns:
        Tuple of (pytest exit code, passed count, failed count)
    """
    report_dir.mkdir(parents=True, exist_ok=True)

    xml_report = report_dir / "report.xml"
    html_report = report_dir / "report.html"
    md_report = report_dir / "report.md"

    print(f"\n{'=' * 60}")
    print(f"Running tests for: {package_name}")
    print(f"Package path: {package_path}")
    print(f"Reports: {report_dir}")
    print(f"{'=' * 60}\n")

    cmd = [
        "uv",
        "run",
        "pytest",
        "-v",
        f"--junitxml={xml_report}",
        f"--html={html_report}",
        "--self-contained-html",
        "--md-report",
        "--md-report-flavor=gfm",
        '--md-report-exclude-outcomes="passed skipped"',
        "--md-report-verbose=1",
        "--md-report-zeros=empty",
        f"--md-report-output={md_report}",
    ]

    result = subprocess.run(cmd, cwd=package_path)

    # Parse the XML report to get test counts
    passed, failed = parse_junit_xml(xml_report)

    return result.returncode, passed, failed


# correspondance nom court <-> répertoire packages
command_packages = {
    "bdd": "pac-bdd",
    "cli": "pac0-cli",
    "pac0": "pac0",
}


@app.command()
def all(
    install_tools: bool = typer.Option(False, help="Installation des outils"),
    install_src: bool = typer.Option(False, help="Installation des sources"),
    repo: str = typer.Option(DEFAULT_REPO, help="URL du dépôt git"),
    branch: str = typer.Option(DEFAULT_BRANCH, help="Branche du dépôt git"),
    pytest_args: Optional[list[str]] = typer.Argument(
        None, help="Arguments pytest après --"
    ),
    ctx: typer.Context = typer.Option(None, hidden=True),
):
    """Lance tous les tests"""
    typer.echo("Lancement de tous les tests...")

    # Track exit codes and test counts
    results = []  # List of (exit_code, passed, failed)

    for k, v in command_packages.items():
        exit_code, passed, failed = one_package_test(
            package_shortname=v,
            install_tools=install_tools,
            install_src=install_src,
            repo=repo,
            branch=branch,
            pytest_args=pytest_args or [],
        )
        results.append((exit_code, passed, failed))

        typer.echo(f"Résultat pour {k}:")
        typer.echo(f"  - Retour code: {exit_code}")
        typer.echo(f"  - Tests passés: {passed}")
        typer.echo(f"  - Tests échoués: {failed}")
        # sample output:
        # ===== 17 failed, 23 passed, 5 skipped, 2 errors in 458.89s (0:07:38) ======

    # Summary
    print(f"\n{'=' * 60}")
    print("Test Summary")
    print(f"{'=' * 60}")

    all_passed = True
    total_ok = 0
    total_ko = 0

    for (pkg_name, _), (code, passed, failed) in zip(command_packages.keys(), results):
        status = "PASSED" if code == 0 else f"FAILED (exit code: {code})"
        print(f"  {pkg_name}: {status} (OK: {passed}, KO: {failed})")
        if code != 0:
            all_passed = False
        total_ok += passed
        total_ko += failed

    total = total_ok + total_ko
    print(f"\nTotal: OK: {total_ok}/{total}, KO: {total_ko}/{total}")
    # print(f"\nReports generated in: {report_base}")
    # print("  - pac0/report.html")
    # print("  - pac0/report.xml")
    # print("  - pac0/report.md")
    # print("  - pac-bdd/report.html")
    # print("  - pac-bdd/report.xml")
    # print("  - pac-bdd/report.md")

    # Return non-zero if any tests failed
    return 0 if all_passed else 1


@app.command(
    name="bdd",
    help="Lance les tests packages/pac-bdd",
)
@app.command(
    name="cli",
    help="Lance les tests packages/pac0-cli",
)
@app.command(
    name="pac0",
    help="Lance les tests packages/pac0",
)
def one_package_test_command(
    install_tools: bool = typer.Option(False, help="Installation des outils"),
    install_src: bool = typer.Option(False, help="Installation des sources"),
    repo: str = typer.Option(DEFAULT_REPO, help="URL du dépôt git"),
    branch: str = typer.Option(DEFAULT_BRANCH, help="Branche du dépôt git"),
    pytest_args: Optional[list[str]] = typer.Argument(
        None, help="Arguments pytest après --"
    ),
    ctx: typer.Context = typer.Option(None, hidden=True),
):
    """
    Lance les tests bdd/pac0/cli

    example:
        uv run pac0 test bdd test_scenario.py::test_flow_des_messages
    est équivalent à :
        uv run pytest -vs test_scenario.py::test_flow_des_messages
    """
    one_package_test(
        package_shortname=ctx.info_name or "bdd",
        install_tools=install_tools,
        install_src=install_src,
        repo=repo,
        branch=branch,
        pytest_args=pytest_args or [],
    )


def one_package_test(
    package_shortname: str,
    install_tools: bool,
    install_src: bool,
    repo: str,
    branch: str,
    pytest_args: list[str],
):
    package_folder = command_packages.get(package_shortname, "pac0")

    typer.echo(
        f"Lancement des tests {package_shortname} dans packages/{package_folder}..."
    )

    base_folder = utils.get_app_base_folder()
    cwd = base_folder / "packages" / package_folder

    report_dir = base_folder / "report" / package_folder
    xml_report = report_dir / "report.xml"
    html_report = report_dir / "report.html"
    md_report = report_dir / "report.md"

    report_dir.mkdir(parents=True, exist_ok=True)

    pytest_cmd = [
        "uv",
        "run",
        "pytest",
        "-v",
        f"--junitxml={xml_report}",
        f"--html={html_report}",
        "--self-contained-html",
        "--md-report",
        "--md-report-flavor=gfm",
        '--md-report-exclude-outcomes="passed skipped"',
        "--md-report-verbose=1",
        "--md-report-zeros=empty",
        f"--md-report-output={md_report}",
    ] + pytest_args

    result = install_run(
        cmd=pytest_cmd,
        repo_url=repo,
        branch=branch,
        tools=["git"],
        install_tools=install_tools,
        install_src=install_src,
        envvar={
            "API_URL": settings.api_url,
            "AWS_ACCESS_KEY_ID": settings.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": settings.aws_secret_access_key,
            "BRIQUE_EXTERNE": "1" if settings.brique_externe else None,
            "NATS_URL": settings.nats_url,
            "S3_BUCKET": settings.s3_bucket,
            "S3_DATA": settings.s3_data,
            "S3_REGION": settings.s3_region,
            "S3_URL": settings.s3_url,
        },
        cwd=cwd,
    )

    # Parse the XML report to get test counts
    passed, failed = parse_junit_xml(xml_report)

    return result, passed, failed
