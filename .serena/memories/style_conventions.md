# Code Style and Conventions

## Formatting
- **Line length:** 100 characters
- **Python version:** 3.11+
- **Formatter:** Ruff (replaces Black)
- **Import sorting:** Ruff (replaces isort)

## Type Hints
- Required for public functions
- Avoid `Any` unless absolutely necessary
- Use `Optional[X]` or `X | None` for nullable types
- Generic collections should be typed: `list[str]`, not `list`
- Use `from __future__ import annotations` for forward references

## Docstrings
- Required for complex functions
- Not needed for trivial getters/setters
- Use imperative mood ("Return the value", not "Returns the value")

## Naming Conventions
- **Classes:** PascalCase
- **Functions/variables:** snake_case
- **Constants:** UPPER_SNAKE_CASE
- **Private:** Leading underscore `_private_method`

## Code Quality
- Small, composable functions over monolithic blocks
- Prefer explicit over implicit
- Maintain backward compatibility unless explicitly breaking
- Never log secrets, tokens, or PII
- Use parameterized queries for Neo4j (prevent injection)

## Ruff Rules Enforced
- `E/W` – pycodestyle errors and warnings
- `F` – pyflakes
- `I` – isort (import sorting)
- `UP` – pyupgrade (modern Python syntax)
- `B` – bugbear (common bugs)
- `C4` – flake8-comprehensions

## Excluded Directories
- `sdk/` and `sdk-web/` are excluded from linting (generated code)

## Import Order
1. Standard library
2. Third-party packages
3. Local packages (logos_*)

## Error Handling
- Raise specific exceptions, not generic Exception
- Include context in error messages
- Log errors with appropriate level
