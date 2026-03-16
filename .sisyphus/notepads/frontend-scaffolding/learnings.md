# Frontend Scaffolding Learnings

## Project Context
- **Project**: madousho.ai (魔导书) - Systematic AI Agent Framework
- **Stack**: Python 3.10+ | SQLAlchemy 2.0 | Pydantic v2 | Typer CLI | FastAPI | Alembic | Loguru
- **Frontend Stack**: Vue 3 + Vite + TypeScript + naive-ui + Pinia + SCSS + MSW + Vitest
- **Package Manager**: pnpm
- **Build Output**: `public/` directory (served by FastAPI)

## Key Decisions
1. **CORS**: Will be solved via Vite proxy (no backend changes needed)
2. **MSW**: Only enabled in development mode via `import.meta.env.DEV`
3. **Auth**: Phase 1 uses placeholder Bearer token interceptor
4. **Scope**: Pure scaffolding - NO pages or components

## Conventions
- Chinese font stack: Noto Sans SC, PingFang SC, Microsoft YaHei
- API base URL: `/api/v1` (proxied to `http://localhost:8000`)
- Build output: `../public` (relative to frontend/)

## Gotchas
- FastAPI already configured to serve static files from `public/`
- Need to ensure MSW doesn't run in production builds
- Vite proxy needed to avoid CORS issues during development
