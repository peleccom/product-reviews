# AGENTS Guidelines for This Repository

Purpose
- Provide concrete, repeatable guidance for agentic contributors and automated agents.
- Cover build/lint/test commands, single-test execution, code style, error handling, and conventions.

Build, Lint, Test Commands
- Dependency install:
  - Use uv (Python project): `uv sync`.
  - `uv run pre-commit install` to set up hooks after initial install.
- Build:
  - Build wheel: `make build` (builds wheel via hatchling).
  - Clean build artifacts: `make clean-build`.
  - Build and publish: `make build-and-publish`.
- Lint and checks:
  - Run all code quality checks: `make check`.
  - Ruff formatter/linter is configured via pyproject.toml; run directly with `uv run ruff check` or format with `uv run ruff format`.
- Tests:
  - Run all tests with coverage: `make test`.
  - Run a single test file: `make test-one TESTS='tests/path/to/test_file.py'`.
  - Direct pytest usage: `uv run python -m pytest -vv -k "pattern" path/to/test.py`.

Provider Testing Architecture
- The package ships a pytest plugin (`src/product_reviews/pytest_plugin.py`) registered via the `pytest11` entry point.
- The plugin auto-generates test items for every provider that defines `test_urls` or `invalid_urls`, with no test files needed.
- Testing infrastructure is organized into three layers:
  - **Testing utilities** (`src/product_reviews/providers/testing/`): Shared code for mock storage, HTTP capture, and validation.
    - `mock_storage.py`: Extensible mock storage abstraction (YAML, JSON) via `MockStorage` ABC.
    - `mock_utils.py`: Mock file management (save, load, clear, validate).
    - `http_capture.py`: HTTP request/response capture and replay utilities.
  - **Pytest plugin** (`src/product_reviews/pytest_plugin.py`): Uses testing utilities to inject auto-generated tests.
- Mock data (recorded HTTP request/response pairs) is stored in **YAML format** for readability and ease of manual editing.
- Record or re-record mocks: `product-reviews test --re-record` (or `--provider <name>` for a single provider).
- Mock files are stored alongside each provider's module in a `mocks/` directory with naming:
  - Valid URLs: `{provider_name}_{url_index}_0.yaml`
  - Invalid URLs: `{provider_name}_invalid_{url_index}_0.yaml`
- **Both valid and invalid URLs are mocked**: All HTTP requests are captured and replayed to ensure deterministic, offline testing.
- The CLI `test` command runs provider tests standalone with rich table output.
- The pytest plugin replays recorded mocks via the `responses` library; tests **fail** (not skip) if no mock data exists.

Code Style Guidelines
- General philosophy: clarity, readability, and maintainability over cleverness.
- Formatting and tools:
  - Enforce Ruff for linting and formatting (configured in pyproject.toml):
    - Target Python 3.9+ (ruff target-version = "py39").
    - Use fix mode and format preview.
    - Run `make check`.
  - Pre-commit hooks enforce linting/formatting on commit.
  - Typer-style static type checking via `ty`.
- Imports:
  - Organize imports via ruff (I rule enabled).
  - Use conventional ordering: stdlib, third-party, local.
  - Prefer absolute imports within the package.
  - All imports should be on global level not function scope. Avoid circular import in a different way
- Naming conventions:
  - Variables and functions: snake_case.
  - Classes: PascalCase.
  - Constants: UPPER_SNAKE_CASE.
- Error handling:
  - Do not swallow errors; add context in exception messages.
  - Use specific exception types; include clear, actionable messages.
  - Logging: prefer structured logs; redact sensitive data.
- Testing philosophy:
  - Unit tests: deterministic, isolated, fast.
  - Integration tests: cover end-to-end flows; use test doubles for externals.
  - Test coverage: configure via pyproject.toml; report XML and term-missing.
  - Fixtures: store in tests/fixtures; regenerate deterministically.
- Documentation:
  - Public APIs require docstrings with examples.
  - Use mkdocs for docs; build with `make docs-test` and serve with `make docs`.
  - Use mkdocstrings to generate API docs from docstrings.
- Security and dependencies:
  - Pin dependencies in lockfile.
  - Scan with deptry; remove obsolete dependencies.
  - Bandit security rules enabled in ruff (S rule set).
- Performance:
  - Avoid unnecessary allocations; prefer simple data structures in hot paths.
- Versioning and deprecation:
  - Semantic versioning in pyproject.toml.
  - Clear changelog for user-facing changes.
- CI/CD expectations:
  - Order: lock check -> pre-commit lint -> ty check -> tests.
  - Cache dependencies with uv.
  - Build via hatchling; publish to PyPI via twine.
- Accessibility (UI):
  - Not applicable (CLI/backend focus), but document a11y considerations for any UI.
- Monorepo considerations:
  - Not currently a monorepo; if extended, maintain workspace isolation per package.
- Code review expectations:
  - Ensure tests for new features; run single-test commands locally.
  - Verify linting and type checks pass.
  - Confirm pre-commit hooks catch issues.

Agent Actions and Verification
- Agents should log a concise summary of actions taken and outcomes.
- Include commands used, environment assumptions, and any noteworthy caveats.
- After changes, run: `make check`, then `make test`, then `make build` to verify no regressions.
- Before committing, ensure `uv run pre-commit run -a` passes.
