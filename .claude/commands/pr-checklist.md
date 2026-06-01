Run through the full PR checklist for this branch before requesting review.

## Pre-merge checks

Work through each item below. Fix any failures before opening or marking the PR ready.

### 1. No secrets committed

```bash
git diff main --name-only | grep -E '\.env'
```

No `.env` files (other than `.env.example`) should appear in the diff.
If any do, remove them and add to `.gitignore` immediately.

### 2. ADR check for matching threshold changes

If this PR changes **anything** in `api/src/screening/` that affects scores,
cutoff thresholds, or the RapidFuzz scorer choice:

- [ ] A new ADR exists at `docs/adr/NNNN-<slug>.md`
- [ ] Its status is `Proposed` (will be set to `Accepted` when merged)
- [ ] The ADR number is referenced in the PR description

If no matching logic changed, skip this item.

### 3. API checks (run from `api/`)

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
```

All three must exit 0. Fix lint and type errors before proceeding.

### 4. UI checks (run from `ui/`)

```bash
pnpm lint
pnpm typecheck
pnpm build
```

All three must succeed. A failing `pnpm build` blocks the CI job and will prevent merge.

### 5. Migration check

If any SQLAlchemy model was added or changed:

```bash
cd api/
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

Commit the generated migration file. Verify it looks correct before committing —
never edit it after it has been applied anywhere.

---

## CI jobs that gate merge

Both jobs must be green before the PR can be merged:

| Workflow file              | Jobs                                    |
|----------------------------|-----------------------------------------|
| `.github/workflows/ci-api.yml` | `lint-typecheck`, `test`            |
| `.github/workflows/ci-ui.yml`  | `lint-typecheck-build`              |

If a CI job fails, check its logs via `gh run view` or the Actions tab.

## Required reviewers (CODEOWNERS)

All changes require approval from **both**:
- `@Faisal-Shamsan`
- `@zone2233`

Do not merge without both approvals.

## PR description template

When opening the PR, fill in `.github/pull_request_template.md`:

```markdown
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
- [ ] Matching thresholds unchanged **or** a new ADR has been added (`docs/adr/NNNN-...`)
- [ ] `uv run ruff check src tests` passes
- [ ] `uv run mypy src` passes (API changes)
- [ ] `pnpm typecheck` passes (UI changes)
- [ ] Migration created if schema changed (`uv run alembic revision --autogenerate`)
```

Link the ADR number in the Summary section if one was written for this PR.
