"""Test that py.typed markers are present in all packages.

This ensures the logos-foundry package is recognized as typed by mypy
when installed as a dependency.

See: https://peps.python.org/pep-0561/
"""

from pathlib import Path

import pytest

# All packages defined in pyproject.toml
PACKAGES = [
    "logos_config",
    "logos_tools",
    "logos_hcg",
    "logos_observability",
    "logos_persona",
    "logos_cwm_e",
    "logos_perception",
    "logos_sophia",
    "logos_test_utils",
    "planner_stub",
]

# Root of the repository
REPO_ROOT = Path(__file__).parent.parent.parent


@pytest.mark.parametrize("package", PACKAGES)
def test_py_typed_marker_exists(package: str) -> None:
    """Each package must have a py.typed marker file for PEP 561 compliance."""
    py_typed_path = REPO_ROOT / package / "py.typed"
    assert py_typed_path.exists(), (
        f"Package '{package}' is missing py.typed marker. " f"Expected at: {py_typed_path}"
    )


def test_all_packages_have_py_typed() -> None:
    """Verify all packages have py.typed - summary test."""
    missing = []
    for package in PACKAGES:
        py_typed_path = REPO_ROOT / package / "py.typed"
        if not py_typed_path.exists():
            missing.append(package)

    assert not missing, (
        f"The following packages are missing py.typed markers: {missing}. "
        "This prevents mypy from recognizing the package as typed when installed."
    )
