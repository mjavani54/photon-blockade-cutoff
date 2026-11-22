"""Check the frozen research files and the archived numerical summaries."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def verify_hashes():
    manifest = json.loads((ROOT / "SHA256SUMS.json").read_text(encoding="utf-8"))
    for name, expected in manifest.items():
        actual = sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch for {name}")
    print(f"Verified SHA-256 for {len(manifest)} research files.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hash-only",
        action="store_true",
        help="check archived bytes using only the Python standard library",
    )
    args = parser.parse_args()
    verify_hashes()
    if args.hash_only:
        return

    output = ROOT / "reproduced" / "validation_record.json"
    subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "code" / "validate_results.py"),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=True,
    )
    print(f"Saved the numerical-summary verification to {output}", flush=True)


if __name__ == "__main__":
    main()
