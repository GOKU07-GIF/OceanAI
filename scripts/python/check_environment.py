"""Print the Python environment expected by OceanAI data tooling.

Run from the repository root:
    python scripts/python/check_environment.py

The script intentionally does not modify the environment. It helps diagnose
cases where Windows resolves `python` to the global interpreter rather than
backend/venv.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VENV_PYTHON = ROOT / "backend" / "venv" / "Scripts" / "python.exe"


def main() -> int:
    print(f"Repository root : {ROOT}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version   : {sys.version.split()[0]}")
    print(f"Expected venv    : {EXPECTED_VENV_PYTHON}")
    print(f"Venv executable exists: {EXPECTED_VENV_PYTHON.exists()}")
    print(f"VIRTUAL_ENV      : {os.environ.get('VIRTUAL_ENV', '<not set>')}")

    for package in ("truststore", "requests", "xarray", "pandas", "pyarrow", "netCDF4"):
        available = importlib.util.find_spec(package) is not None
        print(f"{package:10s}: {'installed' if available else 'MISSING'}")

    if EXPECTED_VENV_PYTHON.exists() and Path(sys.executable).resolve() != EXPECTED_VENV_PYTHON.resolve():
        print()
        print("WARNING: Current Python is not the project's backend/venv interpreter.")
        print("Activate it with:")
        print(r"  .\backend\venv\Scripts\Activate.ps1")
        print("Then run this doctor again.")
        return 2

    print()
    print("Python interpreter matches the project environment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
