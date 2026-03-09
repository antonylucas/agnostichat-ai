# Contributing to AgnostiChat

## Getting Started

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install ruff mypy
   ```
4. Copy environment template:
   ```bash
   cp .env.example .env
   ```
5. Fill in your `.env` values

## Development Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature
   ```
2. Make your changes
3. Run the linter and formatter:
   ```bash
   ruff check . --fix
   ruff format .
   ```
4. Run type checking:
   ```bash
   mypy .
   ```
5. Test locally:
   ```bash
   python app_nicegui.py
   ```
6. Commit, push, and open a pull request against `main`

## Code Style

- Follow ruff configuration in `pyproject.toml`
- Line length: 120 characters
- Add type hints to all new functions
- Write docstrings for all public functions
- Existing code uses Portuguese for identifiers and docstrings — maintain consistency within each file

## Commit Messages

Use conventional commit format:

- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `refactor:` code refactoring
- `chore:` maintenance tasks
- `ci:` CI/CD changes

## Pull Requests

- Keep PRs focused on a single concern
- Include a description of what changed and why
- Ensure CI checks pass before requesting review

## Reporting Issues

Use GitHub Issues. Include:

- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, Docker version)
