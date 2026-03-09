# Contributing to typemap

Thank you for your interest in contributing to typemap!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/nesalia-inc/python-typemap.git
cd python-typemap

# Install dependencies
cd packages/typemap
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_type_eval.py

# Run tests excluding slow tests
uv run pytest --ignore=tests/test_cqa.py
```

## Code Quality

```bash
# Run type checking
uv run mypy src/typemap/

# Run linting
uv run ruff check src/typemap/

# Format code
uv run ruff format src/typemap/
```

## Submitting Changes

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feat/amazing-feature`)
3. **Make** your changes
4. **Run** tests and type checking
5. **Commit** with clear commit messages
6. **Push** to your fork
7. **Open** a Pull Request

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(keyof): add KeyOf type operator

Add support for extracting all member names as tuple of Literals,
similar to TypeScript's keyof operator.

Closes #10
```

## Code Style

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- Follow [PEP 8](https://peps.python.org/pep-0008/) with 100 character line length
- Use type hints for all function signatures
- Write docstrings for public APIs

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include Python version (`python --version`)
- Include minimal reproduction steps
- Include relevant error messages and stack traces

## License

By contributing to typemap, you agree that your contributions will be
licensed under the [MIT License](LICENSE).
