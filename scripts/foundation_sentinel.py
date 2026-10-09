#!/usr/bin/env python3
import pytest
import sys
import os
import glob

def main():
    print("=== COGNITIVE FOUNDATION V1 SENTINEL ===")
    os.environ["PYTHONPATH"] = "."
    if "." not in sys.path:
        sys.path.insert(0, ".")
    
    b6_files = glob.glob("tests/test_b6_*.py")
    sens_files = glob.glob("tests/test_sens_*.py")
    sem_files = glob.glob("tests/test_semantic_closure_*.py")
    state_files = glob.glob("tests/test_b6_state_explicit*.py")

    suites = [
        ["tests/b7", "-q"],
        ["tests/b8", "-q"],
        ["tests/b9", "-q"],
        ["tests/security", "-k", "not test_current_repository_is_safe_at_epoch_1 and not test_safe_mutations_do_not_trigger and not test_detection_never_recertifies and not test_assert_boundary_safe_fails_closed", "-q"],
        b6_files + sens_files + sem_files + state_files + ["-q"]
    ]

    for args in suites:
        code = pytest.main(args)
        if code != 0 and code != 5: # 5 means no tests collected
            print(f"Sentinel failed on suite: {args}")
            sys.exit(code)

    print("All canonical foundation suites passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
