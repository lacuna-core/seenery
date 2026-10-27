# Seenery

Seenery is an experimental project to solve the "semantic search over my photos" problem. The scope is not fully defined and could range from just testing the Google Photos API, building a small layer on top, testing other products and understanding how they work, to evaluating various building blocks for such a solution.

# Commands

```bash
uv sync --dev                        # install all dependencies
uv run pre-commit install            # wire up git hooks (once per clone)

uv run pytest                        # run all tests with coverage
uv run pytest tests/cli/             # run a single test directory
uv run pytest -k test_version        # run a single test by name

uv run ruff check                    # lint (src/ and tests/)
uv run ruff check --fix              # lint with auto-fix
uv run ruff format                   # format
uv run mypy                          # type-check (strict, src/ and tests/)

uv run seenery --help                 # run the CLI
```

# Project structure

`src/seenery/` follows a layered structure:

- **`config.py`** — frozen `Settings` (pydantic-settings, `LACUNA_` env prefix). Calls `load_dotenv()` at import time.
- **`cli/app.py`** — Typer CLI. Sub-command groups live in separate files (e.g. `cli/foo.py`) and are registered via `app.add_typer(...)`.
  - `seenery photos [--days N]` — per-day photo-count report via the Google Photos Picker API.
- **`photos/`** — Google Photos integration:
  - `auth.py` — OAuth installed-app flow (`photospicker.mediaitems.readonly` scope); caches the token at `Settings.google_token_file`.
  - `picker.py` — `PickerClient` (httpx) for the Picker API: create/poll/delete sessions, list picked media items.
  - `models.py` — pydantic models for Picker API responses (camelCase aliases).
  - `report.py` — pure `build_daily_report()` grouping picked photos by day.

### Google Photos API constraints

- Since 2025-03-31 the Library API can only read media created by the app itself, so reading a user's library requires the **Picker API**: the user selects photos in the Google Photos UI, then the app lists them. There is no server-side date filter; `report.py` filters by `createTime`.
- No Google Photos API exposes GPS location (metadata omits it and `=d` downloads strip it), so the report prints `Location: unavailable`.

Logging is configured once in `__init__.py`: loguru handler removed and re-added with the level from `SETTINGS.log_level`. Set `LACUNA_LOG_LEVEL=DEBUG` to see debug output.

## Commit Message Convention

All commits must follow Conventional Commits. See [docs/conventional_commit.md](docs/conventional_commit.md) for the format, allowed types, scopes, and rules.

## Key conventions and guidelines

- Dependency injection: pass config explicitly to any client/service — never read the global `SETTINGS` inside library code.
- mypy is strict. All functions including tests need return type annotations.
- Git hooks (pre-commit) run ruff (fix + format) and mypy on every commit.
- CLI lazy imports: in `cli/app.py`, `seenery.*` imports must be inside the command function body, not at module level. `typer`, `rich`, and stdlib belong at the top of the file. This keeps `--help` fast and isolates heavy deps per command.
- **After every significant change** — new CLI command, new data pipeline, new dependency, changed directory layout — update `CLAUDE.md` (architecture / conventions) and `README.md` (user-facing instructions, dev setup, release process). Keep them in sync with the actual codebase.
