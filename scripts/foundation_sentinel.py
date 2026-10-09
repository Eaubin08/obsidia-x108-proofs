#!/usr/bin/env python3
import pytest
import sys
import os

def main():
    print("=== COGNITIVE FOUNDATION V1 SENTINEL ===")
    os.environ["PYTHONPATH"] = "."
    args = [
        "tests/b7",
        "tests/b8",
        "tests/b9",
        "tests/security",
        "tests/",
        "-k", "b6 or sens or semantic_closure or state_explicit",
        "-q"
    ]
    sys.exit(pytest.main(args))

if __name__ == "__main__":
    main()
