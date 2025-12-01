# Issue beads-59o: Fix test pollution in arda-cli

Status: closed

## User Story

As a developer working on arda-cli,
I want tests to run in isolation without pollution from other tests,
So that I can trust test results and not have flaky test failures.

## Acceptance Criteria

- [x] Each test starts with clean module state
- [x] Config state is reset between tests
- [x] Test pollution no longer causes failures
- [x] All tests pass consistently

## Tasks / Subtasks

- [x] Task 1: Identify sources of test pollution (AC: 1)
  - [x] Analyze test failures in test_conftest.py
  - [x] Trace module-level imports in main.py
  - [x] Identify config cache as root cause
- [x] Task 2: Implement reset_modules() fixture (AC: 2)
  - [x] Create fixture to clear module cache
  - [x] Add autouse decorator for automatic cleanup
  - [x] Test fixture works correctly
- [x] Task 3: Add clean_config_state() autouse fixture (AC: 3)
  - [x] Create fixture to reset config state
  - [x] Use autouse to ensure execution
  - [x] Add to conftest.py
- [x] Task 4: Update tests to use fixtures properly (AC: 4)
  - [x] Verify all tests pass with isolation
  - [x] Check coverage increases

## Architecture Notes

### Context and Constraints

**Root Cause Analysis:**
The main.py module had module-level constants (DEFAULT_THEME, DEFAULT_VERBOSE, DEFAULT_TIMESTAMP) that were computed at import time. When tests imported main.py, these values were cached in the module namespace. The first test to import would set config values, and subsequent tests would inherit this polluted state.

**Solution Pattern:**
- Lazy-loaded defaults: Constants are computed on first access, not import
- Global cache variable: `_default_config_cache` holds computed values
- Reset function: `reset_default_config_cache()` clears cache between tests
- Autouse fixtures: Ensure cleanup happens automatically

### Technical Approach

1. **Modified main.py** (arda_cli/main.py:24-39):
   - Changed constants to lazy-loaded properties
   - Added `_default_config_cache` global variable
   - Added `reset_default_config_cache()` function

2. **Modified conftest.py** (arda_cli/tests/conftest.py:32-72):
   - Added `reset_modules()` fixture to clear sys.modules
   - Added `clean_config_state()` autouse fixture
   - Both fixtures use autouse=True for automatic execution

3. **Created test_conftest.py** (arda_cli/tests/unit/test_conftest.py):
   - 34 new tests covering all fixtures
   - Tests validate fixture behavior
   - Achieved 100% coverage for conftest.py

### Dependencies

- pytest autouse fixtures
- sys.modules manipulation for module clearing
- Global state management in main.py

## Implementation Log

**2025-11-30:** Initial investigation - discovered module-level config cache
**2025-11-30:** Implemented lazy-loaded defaults pattern in main.py
**2025-11-30:** Added reset_modules() and clean_config_state() fixtures to conftest.py
**2025-11-30:** Created comprehensive test suite for conftest.py (34 tests)
**2025-11-30:** Verified all tests pass with clean isolation
**2025-11-30:** Committed changes with bd sync

## References

- [Code: pkgs/arda-cli/arda_cli/main.py](pkgs/arda-cli/arda_cli/main.py)
- [Tests: pkgs/arda-cli/arda_cli/tests/conftest.py](pkgs/arda-cli/arda_cli/tests/conftest.py)
- [Test file: pkgs/arda-cli/arda_cli/tests/unit/test_conftest.py](pkgs/arda-cli/arda_cli/tests/unit/test_conftest.py)
- [Coverage report: just coverage](just coverage)

## Implementation Summary

### Changes Made

Implemented lazy-loaded defaults pattern to prevent test pollution:
- Module-level config cache moved to lazy evaluation
- Added reset_default_config_cache() function for test cleanup
- Created reset_modules() fixture to clear module cache between tests
- Added clean_config_state() autouse fixture to ensure config isolation
- Created comprehensive test suite (34 tests) for conftest.py fixtures

### Files Changed

**Modified:**
- pkgs/arda-cli/arda_cli/main.py - Added lazy-loaded defaults and reset function
- pkgs/arda-cli/arda_cli/tests/conftest.py - Added test isolation fixtures

**Created:**
- pkgs/arda-cli/arda_cli/tests/unit/test_conftest.py - 346 lines, 100% coverage

## Change Log

- 2025-11-30: Fix test pollution with lazy-loaded defaults and autouse fixtures (beads-59o)
- 2025-11-30: Initial context creation
