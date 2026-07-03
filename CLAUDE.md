# CLAUDE.md - my-farm Project Context & Guidelines

## System Rules & Efficiency (Token-Saving)
- **Language**: Respond strictly in English for maximum token density and lowest consumption.
- **Tone**: Extremely concise, direct, and pragmatic. Eliminate conversational fillers, greetings, and apologies.
- **Code Output**: Provide precise code diffs or targeted snippets. Never rewrite unchanged files unless explicitly requested.
- **Assumption**: Assume advanced Python 3.12+ and FastAPI developer expertise. Do not explain basic concepts.

## Model Selection & Prompt Flags
Prefix your prompts with these flags depending on task complexity:
- `[Opus]`: Complex initial integrations (e.g., auth providers like floci/Cognito), structural architecture changes, or deep async debugging.
- `[Sonnet]`: Standard daily feature development, writing new routes/endpoints, schemas, or setting up test suites.
- `[Haiku]`: Quick codebase searches, simple text formatting, dependency updates, or highly repetitive tasks.

## Project Profile & Stack
- **Project Name**: `my-farm`
- **Framework**: FastAPI (Async)
- **API Documentation**: Scalar UI via `scalar-fastapi` mounted strictly at `/docs-scalar`.
- **Dependency Manager**: Poetry (Virtual environment `.venv` located in project root).
- **ASGI Server**: Uvicorn.

## Core Development Commands
```bash
poetry config virtualenvs.in-project true             # Ensure .venv is created in-project
poetry install                                       # Install project dependencies
poetry run uvicorn app.main:app --reload              # Run local API with auto-reload