## Summary
<!-- What does this PR do? Link the related issue if applicable. -->

## Type of change
- [ ] Bug fix
- [ ] New feature / endpoint
- [ ] Refactor
- [ ] Documentation / ADR

## Testing
- [ ] Added / updated unit tests
- [ ] Manually tested locally (`docker compose up`)

## Checklist
- [ ] No `.env` files committed
- [ ] Matching thresholds unchanged **or** a new ADR has been added to `docs/adr/`
- [ ] `uv run ruff check src tests` passes
- [ ] `uv run mypy src` passes (API changes)
- [ ] `pnpm typecheck` passes (UI changes)
- [ ] Migration created if schema changed (`uv run alembic revision --autogenerate`)
