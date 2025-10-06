#!/usr/bin/env python3
"""
Test runner for Virtual Cow Tipper
Runs all test suites and reports results
"""
import subprocess
import sys

test_files = [
    'tests/test_cow_generation.py',
    'tests/test_item_factory.py',
    'tests/test_dialogue_manager.py',
    'tests/test_game_integration.py',
]

def run_test(test_file):
    """Run a single test file and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=10
        )

        print(result.stdout)

        if result.returncode != 0:
            print("STDERR:", result.stderr)
            return False

        return True
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {test_file} took too long")
        return False
    except Exception as e:
        print(f"ERROR running {test_file}: {e}")
        return False


def main():
    print("="*60)
    print("VIRTUAL COW TIPPER - TEST SUITE")
    print("="*60)

    results = {}
    for test_file in test_files:
        results[test_file] = run_test(test_file)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_file, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {status:6} - {test_file}")

    print(f"\nResults: {passed}/{total} test suites passed")

    if passed == total:
        print("\nALL TESTS PASSED! Game is ready to play.")
        return 0
    else:
        print(f"\n{total - passed} test suite(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
