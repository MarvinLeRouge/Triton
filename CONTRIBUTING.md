[🇫🇷 Version française](CONTRIBUTING.fr.md) | 🇬🇧 English version

---

# Contributing to Triton

This is primarily a personal project. External contributions (bug reports,
fixes, small improvements) are welcome but limited in scope.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- Node.js ≥ 22
- Docker with Compose v2 (`docker compose`), for the full stack via Traefik

## Local setup

```bash
git clone https://github.com/MarvinLeRouge/Triton.git
cd Triton
uv sync
cd frontend && npm install
```

## Running tests

```bash
uv run pytest              # backend
cd frontend && npm run test:unit   # frontend
```

## Workflow

1. Fork the repository and create a branch off `develop` (not `main`, which is
   protected and only receives merges at the end of a completed phase).
2. Make your change, with tests covering it.
3. Commit following the convention below.
4. Push and open a pull request against `develop`.
5. CI must pass before review.

## Branch naming

| Type | Prefix |
|---|---|
| Phase feature (roadmap work) | `phase-{n}-{phase-name}/feat/{feature-name}` |
| Feature (outside a roadmap phase) | `feat/short-description` |
| Bug fix | `fix/short-description` |
| Chore | `chore/short-description` |
| Documentation | `docs/short-description` |
| Refactor | `refactor/short-description` |
| Tests | `test/short-description` |

Use lowercase kebab-case. No special characters.

## Commit convention

Follow [Conventional Commits](https://www.conventionalcommits.org/), imperative
mood, lowercase summary, no trailing period, with a mandatory `Modified files:`
section:

```
type(scope/module): short description

Modified files:
- path/to/file-a.ext - what was changed
- path/to/file-b.ext - what was changed
```

Scope must always specify `backend/<module>`, `frontend/<module>`, `infra`, or
`root` — never a bare `type: ...`.

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`, `ci`.

Examples:

```
feat(backend/engine): add grid initialization
fix(frontend/canvas): correct heatmap color scale
docs(root): add CONTRIBUTING.md
```

## Code style

Backend (Python):

```bash
uv run ruff check .        # lint
uv run ruff format --check .
uv run mypy engine api     # strict type-checking
```

Frontend (TypeScript/Vue):

```bash
cd frontend
npm run lint               # ESLint + oxlint
npm run type-check         # vue-tsc
```

CI will reject any pull request that fails these checks.

## Releases and changelog

The `[Unreleased]` section of `CHANGELOG.md` is maintained automatically: a CI
workflow (`.github/workflows/changelog.yml`, config in `cliff.toml`) runs
[git-cliff](https://git-cliff.org/) on every push to `main` and opens or
updates a pull request with the regenerated section. Never hand-edit
`CHANGELOG.md`'s `[Unreleased]` section or anything above it; entries before
`v0.6.0` are frozen hand-written history.

To cut an actual release, once `main` reflects the state you want to ship:

1. Create an annotated tag: `git tag -a vX.Y.Z -m "Phase N: Title"`.
2. Push it: `git push origin vX.Y.Z`.
3. Locally, regenerate the changelog with the new version title:
   `npx git-cliff --config cliff.toml --tag vX.Y.Z --prepend CHANGELOG.md`
   (after removing any stale `[Unreleased]` block), then commit the result.

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating,
you are expected to uphold it.

## License

By contributing, you agree that your contributions will be licensed under the
project's license (see [LICENSE](LICENSE)).
