# Contributing to Arda

Thank you for your interest in contributing to Arda! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branch Strategy](#branch-strategy)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Code Style](#code-style)
- [Testing](#testing)
- [Security](#security)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to the principles of open collaboration, respect, and constructive feedback. Please be professional and courteous in all interactions.

## Getting Started

### Prerequisites

- NixOS or Nix-enabled Linux distribution
- Git
- Age encryption tool (for secrets management development)
- Python 3.13+ (for CLI development)
- Node.js 18+ (for pre-commit hooks)

### Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/lorddevi/arda-core.git
cd arda-core

# Install development dependencies
nix develop

# Install pre-commit hooks (REQUIRED for all commits)
pre-commit install

# Verify the setup
nix flake check
```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch from `arda-v1` for your work:

```bash
# Update your local arda-v1 branch
git checkout arda-v1
git pull origin arda-v1

# Create a new feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/your-bugfix
# or
git checkout -b experiment/your-experiment
```

### 2. Make Changes

- Follow the coding standards (see [Code Style](#code-style))
- Write tests for new functionality
- Update documentation as needed
- Run pre-commit hooks before committing

### 3. Commit Changes

We use conventional commits for clear history:

```bash
git add .
git commit -m "feat: add new service template for postgresql"
```

See [Commit Messages](#commit-messages) for more details.

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
# Then create a Pull Request on GitHub
```

## Branch Strategy

### Primary Branches

- **`arda-v1`**: Main development branch. All new features and fixes are merged here first.
- **`clan-core`**: Reference branch containing upstream clan-core code. Used for code extraction and comparison.

### Feature Branches

- **`feature/*`**: New features or significant enhancements
  - Examples: `feature/service-feature-role-hierarchy`, `feature/secret-rotation`
  - Merge strategy: Squash and merge to arda-v1

### Maintenance Branches

- **`bugfix/*`**: Bug fixes for specific issues
  - Examples: `bugfix/nix-build-failure`, `bugfix/secrets-decryption`
  - Merge strategy: Squash and merge to arda-v1

### Experimental Branches

- **`experiment/*`**: Proof-of-concept work or exploratory development
  - Examples: `experiment/zfs-support`, `experiment/argo-cd-integration`
  - May or may not be merged, depending on results

### Version Branches (when needed)

- **`release/vX.Y.Z`**: Release preparation branches
  - Only created when preparing official releases
  - Final release tags created from these branches

### Branch Naming Conventions

```bash
{type}/{short-description}

Types:
- feature: New functionality
- bugfix: Bug fixes
- hotfix: Critical production fixes
- experiment: Exploratory work
- docs: Documentation updates
- chore: Maintenance tasks
```

Examples:

- `feature/web-server-role`
- `bugfix/age-key-rotation`
- `docs/readme-improvements`

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear, consistent commit messages.

### Format

```bash
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools
- `perf`: A code change that improves performance
- `ci`: Changes to CI configuration files and scripts

### Examples

```bash
# Feature
feat(cli): add web-server role definition

# Bug fix
fix(secrets): handle age key rotation edge case

# Documentation
docs(readme): add quick start guide

# Refactoring
refactor(roles): simplify role composition logic

# Breaking change
feat(cli)!: remove deprecated host create command

# Multiple types
feat(cli): add new templates
docs: update API documentation
test: add integration tests for templates
```

## Pull Requests

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Pre-commit hooks pass
- [ ] Tests pass (`nix flake check`)
- [ ] Documentation is updated (if needed)
- [ ] Commit messages follow conventional commit format
- [ ] Branch is up-to-date with arda-v1

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #issue-number

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

### Review Process

1. **Automated Checks**: CI/CD runs automatically (Nix builds, tests, linters)
2. **Code Review**: At least one maintainer reviews for:
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Security considerations
3. **Testing**: Manual testing may be required for complex changes
4. **Approval**: Changes must be approved before merging

### Merge Strategies

- **Feature/Bugfix Branches**: Squash and merge
- **Large Features**: May use merge commit for preserving history
- **Hotfixes**: Fast-forward or squash merge

## Code Style

### Python (arda-cli)

We use standard Python tools with specific configurations:

```bash
# Formatting
black . --line-length 88

# Linting
flake8 . --max-line-length 88 --extend-ignore E203,W503

# Type checking (optional but recommended)
mypy pkgs/arda-cli/
```

Configuration files:

- `.flake8`: Flake8 configuration
- `pyproject.toml`: Black and project metadata

### Nix

We use `nixpkgs-fmt` for formatting:

```bash
nix fmt
```

Or manually:

```bash
nixpkgs-fmt .
```

### General Guidelines

- Follow PEP 8 for Python
- Use meaningful variable and function names
- Write docstrings for all public functions
- Keep functions small and focused
- Prefer composition over inheritance
- Write tests for new functionality

## Testing

### Test Structure

```bash
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
└── e2e/              # End-to-end tests
```

### Running Tests

```bash
# All tests
nix flake check

# Specific test suite
pytest tests/unit/

# With coverage
pytest --cov=pkgs/arda-cli tests/
```

### Writing Tests

- Unit tests should be fast and isolated
- Integration tests should test component interactions
- End-to-end tests should verify complete workflows
- Use pytest fixtures for setup/teardown
- Mock external dependencies

## Security

### Secret Detection

This project uses `detect-secrets` to prevent accidental secret commits:

```bash
# Install pre-commit hooks (runs detect-secrets automatically)
pre-commit install

# Manual scan
detect-secrets scan --baseline .secrets.baseline
```

### Reporting Security Issues

**Do not** create public issues for security vulnerabilities.

Instead:

- Email: [your-secure-email@example.com]
- Include: Description, steps to reproduce, potential impact
- You will receive acknowledgment within 48 hours

### Secure Development Practices

- Never commit secrets, keys, or passwords
- Use the secret management system for all secrets
- Review code before committing for potential data leaks
- Follow the principle of least privilege

## Documentation

### Types of Documentation

1. **API Documentation**: Docstrings in code
2. **User Guides**: How-to guides in `docs/user/`
3. **Architecture**: Design documents in `docs/architecture/`
4. **Development**: Developer guides (this document)

### Writing Documentation

- Use clear, concise language
- Provide examples for complex concepts
- Keep documentation up-to-date with code changes
- Use markdown formatting consistently
- Include diagrams where helpful

### Documentation Tools

- Markdown for most documentation
- Mermaid for diagrams
- Sphinx for API documentation (future)

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for general questions
- Review existing issues and discussions first

## Recognition

Contributors will be recognized in:

- README.md contributors section
- CHANGELOG.md
- Release notes

Thank you for contributing to Arda! 🎉
