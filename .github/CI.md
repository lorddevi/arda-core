# Continuous Integration (CI) Setup

This document describes the CI/CD setup for the arda-core project.

## GitHub Actions Workflow

The CI is configured in `.github/workflows/test.yml` and runs automatically on:

- Push to `main`, `master`, or `testing` branches
- Pull requests to `main`, `master`, or `testing` branches

## Jobs

### 1. Fast Validation

- **Triggers**: All pushes and PRs
- **Purpose**: Quick validation without running full test suite
- **Steps**:
  - Check flake validity (`nix flake check`)
  - Run pre-commit hooks (linting, formatting)
  - **Duration**: ~1-2 minutes

### 2. Fast Tests

- **Triggers**: All pushes and PRs
- **Purpose**: Build package and run fast unit tests
- **Steps**:
  - Build `arda-cli` package (runs fast tests during build)
  - Upload test artifacts
- **Duration**: ~2-3 minutes

### 3. All Tests

- **Triggers**: All pushes and PRs
- **Purpose**: Run complete test suite (excluding VM tests)
- **Steps**:
  - Execute `just test-all` (runs all non-VM tests)
  - Upload coverage reports and test results
- **Duration**: ~3-5 minutes

### 4. VM Tests

- **Triggers**: Manual dispatch or scheduled (nightly)
- **Purpose**: Run VM-based integration tests
- **Steps**:
  - Execute `just test-vm` (requires VM support)
  - Upload VM test artifacts
- **Duration**: ~5-10 minutes
- **Note**: Not run on regular PRs due to resource requirements

### 5. Build Documentation

- **Triggers**: All pushes and PRs
- **Purpose**: Build and archive CLI binary
- **Steps**:
  - Build `arda-cli` package
  - Upload binary as artifact
- **Duration**: ~2-3 minutes

### 6. Summary

- **Triggers**: After all test jobs complete
- **Purpose**: Aggregate test results and display summary
- **Output**: Test results summary in PR comments and commit status

## Required GitHub Secrets

The following secrets need to be configured in the repository settings:

### CACHIX_AUTH_TOKEN

- **Purpose**: Enable binary cache for faster CI builds
- **How to get**:
  1. Sign up at [cachix.org](https://cachix.org)
  2. Create a cache named `arda-core`
  3. Generate an auth token
  4. Add to GitHub repository secrets
- **Optional**: CI will work without this, but builds will be slower

### How to Add Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add `CACHIX_AUTH_TOKEN` with your token value

## Testing CI Locally

### Using act (Optional)

You can test the GitHub Actions workflow locally using [act](https://github.com/nektos/act):

```bash
# Install act
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run specific job
act -j validate

# Run all jobs
act

# Run with secrets (create .secrets file)
act --secret-file .secrets
```

### Manual Verification

Before pushing, verify locally:

```bash
# Run all checks
nix flake check

# Run fast tests
nix build .#arda-cli

# Run all tests
nix develop --command just test-all

# Run pre-commit
nix develop --command pre-commit run --all-files
```

## Caching

The CI uses two levels of caching:

### 1. Nix Build Cache

- Automatically caches build artifacts
- Enabled via Nix's built-in caching
- Restores on subsequent runs

### 2. Cachix (Optional)

- Distributed binary cache
- Significantly speeds up CI
- Requires `CACHIX_AUTH_TOKEN` secret
- Configured in workflow with:

  ```yaml
  - name: Setup cachix
    uses: cachix/cachix-action@v14
    with:
      name: arda-core
      authToken: ${{ secrets.CACHIX_AUTH_TOKEN }}
  ```

## Artifacts

CI uploads the following artifacts:

- **Fast test results**: `fast-test-results/`
  - Build outputs
  - Unit test reports

- **All test results**: `test-results/`
  - Coverage reports (HTML, XML)
  - JUnit XML test results
  - Build outputs

- **VM test results**: `vm-test-results/`
  - VM test logs
  - Build outputs

- **CLI binary**: `arda-cli/`
  - Final built binary for download

## Concurrency Control

The workflow uses concurrency groups to:

- Cancel in-progress runs on new pushes
- Prevent resource waste
- Ensure latest commits take precedence

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Branch Protection

Recommended branch protection rules for `main`:

- Require status checks to pass:
  - `Fast Validation`
  - `Fast Tests`
  - `All Tests`
- Require branches to be up to date
- Restrict pushes to administrators
- Require review from code owners

## Troubleshooting

### Common Issues

1. **Flake check fails**
   - Run `nix flake check` locally
   - Ensure all Nix files are formatted

2. **Pre-commit fails**
   - Run `pre-commit run --all-files` locally
   - Fix linting/formatting issues

3. **Tests fail**
   - Check test results in CI artifacts
   - Reproduce locally with `just test-all`

4. **Build timeout**
   - Check for infinite loops in code
   - Verify test markers (fast vs slow)

5. **VM tests fail**
   - VM tests are optional on PRs
   - Check nightly scheduled runs
   - May require different platform

### Getting Help

- Check workflow logs in GitHub Actions tab
- Review artifacts for detailed test output
- Enable debug logging:

  ```yaml
  - name: Run all tests
    run: nix develop --command just test-all
    env:
      CI_DEBUG: true
  ```

## Benefits

✅ **Automated Testing**: Every push/PR runs full test suite
✅ **Fast Feedback**: Quick validation in 1-2 minutes
✅ **Coverage**: Automatic coverage reporting
✅ **Artifacts**: Downloadable binaries and test results
✅ **Caching**: Faster builds with binary cache
✅ **Branch Protection**: Ensures code quality
✅ **Documentation**: Comprehensive test results
✅ **Flexibility**: Separate jobs for different test types

## Maintenance

- Update Nix channels periodically
- Review and update dependencies
- Monitor CI performance and costs
- Rotate secrets annually
- Update GitHub Actions versions quarterly
