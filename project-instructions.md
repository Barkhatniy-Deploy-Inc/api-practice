<!-- template-version: 2 -->
# Зебра-стат Project Instructions

## Core Principles

### I. Test-First (TDD)

All feature development MUST follow the Test-Driven Development lifecycle (Red-Green-Refactor) using pytest. — This ensures correctness, facilitates safe refactoring, and guarantees that every implementation detail is verified by an automated test.

### II. Simplicity (YAGNI)

System MUST avoid early over-engineering by implementing only the features required for the current task. — "You Ain't Gonna Need It" preserves maintainability and prevents code bloat. Use standard FastAPI/Pydantic types first.

### III. Security-First

All endpoints MUST be protected by default. Public exceptions MUST be explicitly registered in a dedicated router. — Protects sensitive traffic accident data and prevents unauthorized access to the analytics engine.

### IV. Strict Typing

All code MUST use explicit Python type hints and Pydantic v2 models for data validation. — Catches logical errors at development time and provides robust runtime validation for API inputs/outputs.

### V. Agent Output Style

All agent output MUST be concise and outcome-oriented. This principle supersedes any verbose defaults.

- **Progress reports**: Facts and outcomes only — no narration, no restating the task.
- **Artifacts**: Emit required sections only — no preamble paragraphs, no summary epilogues.
- **Reasoning**: Omit unless the user asks "why" or the decision is non-obvious.
- **Errors / blockers**: State the problem, the attempted fix, and the result — nothing else.
- **Phase-boundary reports**: ≤ 5 bullet points.
- **Preserve without compressing**: Artifact template structure and required sections; explicit decision / registration / validation guidance in shared skills; delegation constraints and sub-agent role definitions; existing size limits (spec ≤ 10 KB, research ≤ 4 KB, stories ≤ 200 words).

## Technology Stack

- **Language/Runtime**: Python 3.10
- **Frameworks**: FastAPI, SQLAlchemy 2.0 (Async)
- **Storage**: SQLite (aiosqlite)
- **Infrastructure**: Docker, Docker Compose

## Testing & Quality Policy

- **Coverage Target**: 100%
- **Required QC Categories**: linting, security scanning, coverage
- **Test Strategy**: TDD strict (red-green-refactor); Unit + Integration tests with httpx.AsyncClient; DB isolation via rollback fixtures.
- **Linting / Formatting**: Ruff strict

## Source Code Layout

- **Policy**: PRESERVE_EXISTING_LAYOUT
- **Convention**: Source code under /app; scripts in /scripts; tests in /tests; documentation in /docs.

## Development Workflow

- **Branching**: GitHub Flow (feature branches from main, squash merge)
- **Commit Convention**: Conventional Commits
- **CI Requirements**: All tests pass (100% coverage), Ruff lint clean, Safety/Bandit security scan pass.

## Governance

- Project instructions supersede all other documentation and practices.
- Amendments require a version bump with ISO-dated changelog entry.
- All implementations MUST pass the Instructions Check gate during planning.
- Complexity beyond these principles MUST be justified and documented.
- **API Security**: Salt changes invalidate all existing student keys. Modification of AUTH_SALT requires a planned migration track.

**Version**: 1.0.0 | **Last Amended**: 2026-04-24
