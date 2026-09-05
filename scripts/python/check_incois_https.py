"""Diagnose Windows HTTPS trust for the public INCOIS ERDDAP endpoint.

Run inside the OceanAI virtual environment:
    python scripts/python/check_incois_https.py

This uses the native Windows certificate store through truststore instead of
weakening TLS verification with verify=False.
"""

from __future__ import annotations

import sys

try:
    import truststore
except Exception as exc:
    raise SystemExit(
        "Could not import truststore.\n"
        f"Python executable: {sys.executable}\n"
        f"Python version: {sys.version}\n"
        f"Import error: {type(exc).__name__}: {exc}\n"
        "Run: python -m pip install --force-reinstall truststore==0.10.4"
    ) from exc

truststore.inject_into_ssl()

import requests

URL = "https://erddap.incois.gov.in/erddap/info/NOAA_AVHRR_AMSR_datasets/index.html"


def main() -> None:
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"truststore: {getattr(truststore, '__version__', 'installed')}")
    print(f"Testing: {URL}")
    try:
        response = requests.get(URL, timeout=30)
        print(f"HTTPS status: {response.status_code}")
        print(f"Resolved URL: {response.url}")
        print("INCOIS HTTPS connection is working.")
    except requests.exceptions.SSLError as exc:
        print("TLS verification failed.")
        print(str(exc))
        print(
            "Install the organization/antivirus proxy CA into the Windows trusted "
            "root store if this machine intercepts HTTPS. Do not disable certificate verification."
        )
        raise SystemExit(2)
    except requests.RequestException as exc:
        print("INCOIS request failed after TLS setup:")
        print(str(exc))
        raise SystemExit(3)


if __name__ == "__main__":
    main()
