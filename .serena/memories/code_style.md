# Code Style and Conventions

## Python Style

- **Python version**: >=3.11
- **Line length**: 88 characters (Black-compatible)
- **Quotes**: Double quotes
- **Indentation**: Spaces (not tabs)
- **Imports**: Absolute imports, grouped (stdlib/third-party/local), sorted by isort

## Type Hints (REQUIRED)

- Strict MyPy: `disallow_untyped_defs=true`
- All functions must have type annotations
- Use `Optional[T]` explicitly (no implicit None)

## Naming Conventions

- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

## Docstrings

- Required for public functions and classes (D101, D102, D103)
- Not required for `__init__`, magic methods, modules, packages

## CLI Patterns

- Use Click + rich-click for CLI commands
- Rich error panels for user-facing errors
- Pydantic for configuration validation

## Test Conventions

- Use pytest markers: `fast`, `slow`, `unit`, `integration`, `cli`, `vm`, `with_core`, `without_core`
- Tests run in isolation (module state reset between tests)
- assert is allowed (S101 ignored)

## Ruff Rules Enabled

- E, W: pycodestyle
- F: pyflakes
- I: isort
- N: pep8-naming
- D: pydocstyle
- UP: pyupgrade
- B: flake8-bugbear
- C4: flake8-comprehensions
- S: bandit (security)
- T20: flake8-print (T201 allowed)
- RUF: Ruff-specific
