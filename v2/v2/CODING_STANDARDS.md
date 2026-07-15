# Coding Standards

## Python (Backend & Engine)

- **Formatter**: Ruff (replaces Black/isort)
- **Linter**: Ruff with E, F, I, N, UP, B, SIM rules
- **Typechecker**: MyPy strict mode
- **Line length**: 100 characters
- **Imports**: Sorted by Ruff (isort rules)
- **Docstrings**: Google style for public functions/classes
- **Type hints**: Required for all function signatures
- **Naming**:
  - `snake_case` for functions/variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

## TypeScript (Frontend)

- **Formatter**: Prettier
- **Linter**: ESLint with strict TypeScript rules
- **TypeScript**: Strict mode enabled
- **Line length**: 100 characters
- **Imports**: Absolute imports with `@/` alias
- **Naming**:
  - `camelCase` for functions/variables
  - `PascalCase` for components/interfaces
  - `UPPER_CASE` for constants

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

## Git

- Never force push to `main` or `develop`
- Keep commits atomic and focused
- Rebase before merging to keep history clean
