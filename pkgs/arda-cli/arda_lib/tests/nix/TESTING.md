# Nix Operations Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for Nix operations in the ARDA CLI project. The test suite validates all Nix-related functionality, ensuring reliability, performance, and preventing regressions.

## Testing Architecture

### Test Structure

The test suite is organized into four main categories:

1. **Unit Tests** (`TestNixExceptions`, `TestNixCommand`, `TestNixEval`, `TestNixBuild`, `TestNixShell`, `TestNixMetadata`, `TestNixConfig`, `TestNixStore`)
   - Test individual functions and methods
   - Fast execution with mocked dependencies
   - Validate error handling and edge cases

2. **Integration Tests** (`TestFlakeCacheIntegration`)
   - Test full workflows across multiple components
   - Validate cache persistence and loading
   - Test cache invalidation and re-initialization

3. **Component Tests** (`TestFlakeClass`, `TestPackagesClass`, `TestFlakeCacheEntry`, `TestFlakeCache`)
   - Test individual classes and their interactions
   - Validate caching logic and data structures

4. **Specialized Tests**:
   - **Error Handling** (`TestFlakeCacheErrorHandling`): Malformed outputs, error propagation
   - **Edge Cases** (`TestFlakeCacheEdgeCases`): Special characters, long selectors, duplicates
   - **Performance** (`TestFlakeCachePerformance`): Hit/miss ratios, memory usage, disk I/O
   - **Thread Safety** (`TestFlakeCacheThreadSafety`): Concurrent access patterns
   - **Core Functionality** (`TestFlakeCacheCoreFunctionality`): Cache operations integration

## Test Execution Strategy

### Mock-Based Testing

The majority of tests use `unittest.mock.patch` to mock Nix commands, providing:

- **Reproducibility**: Tests run consistently without external dependencies
- **Speed**: No actual Nix operations required
- **Safety**: No risk of corrupting system state
- **Control**: Precise control over command outputs and errors

Example pattern:
```python
@patch('subprocess.run')
def test_nix_operation(mock_run):
    mock_run.return_value.stdout = json.dumps({"key": "value"})
    # Test implementation
```

### Real Nix Command Testing

Some tests execute actual Nix commands when safe to do so:

- **Skip Logic**: Tests check `select_source().exists()` before running
- **Isolated Environment**: Tests use `ARDA_TEST_STORE` and `IN_NIX_SANDBOX` for isolation
- **Explicit Opt-In**: Tests decorated with `@pytest.mark.skipif` for conditional execution

Example:
```python
@pytest.mark.skipif(not select_source().exists(), reason="nix-select library not built")
def test_real_nix_operation():
    # Actual Nix command execution
```

## Feature-Specific Testing

### 1. Nix-Select Integration Testing (`TestSelectorParsing`)

Tests validate:
- Simple selector parsing (`packages.flake`): Basic dot-notation paths
- Wildcard selectors (`packages.*`): Pattern matching across attributes
- Set selectors (`{alt1,alt2,alt3}`): Multiple alternative paths
- Optional selectors (`?optionalFeature`): Graceful handling of missing attributes
- JSON serialization: Proper encoding/decoding of selector objects

### 2. Test Store Isolation Testing (`TestNixTestStore`)

Tests validate:
- **ARDA_TEST_STORE environment variable**: Correct store path usage
- **IN_NIX_SANDBOX behavior**: Sandboxed execution in temporary stores
- **Concurrent test execution**: Thread-safe access to isolated stores
- **Context manager integration**: Proper store locking and cleanup

### 3. Gcroot Management Testing (`TestGcrootManagement`)

Tests validate:
- **nix_add_to_gcroots()**: Adding store paths to garbage collection roots
- **Store path references**: Finding all Nix store references in strings
- **Physical path resolution**: Following symlinks to actual store paths
- **Sandbox compatibility**: Correct behavior in isolated test environments
- **Error handling**: Invalid paths, missing files, permission errors

### 4. Flake Caching Testing (8 test classes)

Tests validate the complete caching lifecycle:

**Cache Operations**:
- Cache hit/miss behavior: Fast lookups vs. Nix evaluation
- Cache persistence: Saving/loading cache to/from disk
- Selective invalidation: Removing specific entries while preserving others
- Atomic writes: Safe cache updates without corruption

**Performance Characteristics**:
- Cache hit performance: Sub-millisecond lookups
- Memory usage: Bounded cache growth with LRU eviction
- Disk I/O: Efficient JSON serialization/deserialization
- Concurrent access: Thread-safe operations under load

**Edge Cases**:
- Special characters: Unicode, quotes, brackets in selectors
- Long selectors: Strings exceeding 100 characters
- Duplicate selectors: Handling repeated selections
- Empty selectors: Graceful handling of invalid input
- Corrupted cache: Recovery from invalid JSON or missing files
- Nested operations: Preventing infinite recursion

## Test Coverage Metrics

### Current Coverage

- **nix.py**: 81% coverage (620 lines total, 116 uncovered)
- **test_nix.py**: 94% coverage (1765 lines total, 113 uncovered)
- **Overall**: 90% coverage across test modules

### Coverage Goals

- **Minimum threshold**: 80% for nix.py
- **Target**: 85% for production code
- **Uncovered lines**: Documented and justified (mostly error paths)

### Uncovered Line Categories

Most uncovered lines are intentional:
- **Error handlers**: Rare error conditions difficult to trigger
- **Debug code**: Development-only paths
- **Platform-specific code**: OS-dependent functionality

## Test Execution

### Running Tests

```bash
# Run all Nix tests
pytest pkgs/arda-cli/arda_lib/tests/nix/test_nix.py -v

# Run with coverage
pytest --cov=pkgs/arda-cli/arda_lib/nix/nix \
       --cov-report=term-missing \
       pkgs/arda-cli/arda_lib/tests/nix/test_nix.py

# Run only fast (mocked) tests
pytest -m "not slow" pkgs/arda-cli/arda_lib/tests/nix/test_nix.py

# Run only real Nix tests (requires nix-select library)
pytest -m "slow" pkgs/arda-cli/arda_lib/tests/nix/test_nix.py
```

### CI/CD Integration

Tests run automatically on:
- **Pull requests**: Full test suite with coverage
- **Main branch**: All tests including real Nix operations
- **Pre-commit hooks**: Fast subset with formatting and linting

## Testing Best Practices

### 1. Test Organization
- Group related tests in dedicated test classes
- Use descriptive test method names: `test_operation_scenario_expected_result`
- Follow AAA pattern: Arrange, Act, Assert

### 2. Mock Management
- Patch at the highest level (module boundary)
- Reset mocks between tests
- Use context managers for cleanup

### 3. Test Data
- Use factories for complex objects
- Avoid magic numbers
- Use fixtures for shared setup

### 4. Assertion Strategy
- Test one behavior per test
- Use specific assertions (not generic `assertTrue`)
- Validate both positive and negative cases

### 5. Documentation
- Document complex test scenarios
- Explain non-obvious test choices
- Reference relevant issues/commits

## Continuous Improvement

### Test Metrics Tracked
- Test count over time
- Coverage trends
- Flaky test detection
- Execution time monitoring

### Regular Reviews
- **Weekly**: Test execution times, flaky tests
- **Monthly**: Coverage analysis, missing edge cases
- **Quarterly**: Testing strategy review and updates

## References

- **Implementation**: `pkgs/arda-cli/arda_lib/nix/nix.py`
- **Tests**: `pkgs/arda-cli/arda_lib/tests/nix/test_nix.py`
- **Integration Tests**: `pkgs/arda-cli/arda_lib/tests/integration/`
- **Coverage Reports**: Generated with `pytest --cov`

## Conclusion

This testing strategy ensures:
- **Reliability**: All Nix operations thoroughly validated
- **Maintainability**: Tests serve as executable documentation
- **Performance**: Cache operations meet SLAs
- **Safety**: Concurrent operations don't corrupt state
- **Coverage**: 81% code coverage with justified exceptions

The test suite provides confidence in the Nix operations layer, enabling safe refactoring and feature development.
