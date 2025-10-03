# Contributing to RuleIQ

Thank you for your interest in contributing to RuleIQ! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Quality Standards](#code-quality-standards)
- [TODO Policy](#todo-policy)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Security](#security)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 22+
- Docker and Docker Compose
- Git

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/OmarA1-Bakri/ruleIQ.git
   cd ruleIQ
   ```

2. **Install pre-commit hooks**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

3. **Set up environment**:
   ```bash
   cp env.template .env.local
   # Edit .env.local with your configuration
   ```

4. **Install dependencies**:
   ```bash
   # Backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   pnpm install
   ```

See [docs/ENVIRONMENT_SETUP.md](docs/ENVIRONMENT_SETUP.md) for detailed setup instructions.

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates
- `test/description` - Test additions/updates

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(api): add evidence recommendation endpoint
fix(auth): resolve JWT token expiration issue
docs(readme): update installation instructions
refactor(assistant): extract provider layer
test(api): add integration tests for chat endpoints
```

## Code Quality Standards

### Python

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use docstrings for classes and functions
- Run linters: `ruff check .`

### TypeScript/React

- Follow [Airbnb Style Guide](https://github.com/airbnb/javascript)
- Use TypeScript strict mode
- Prefer functional components with hooks
- Use meaningful variable names
- Run linters: `pnpm lint`

### File Size Limits

- **Maximum file size**: 500 lines
- **Recommended**: 200-300 lines per file
- If a file exceeds 500 lines, refactor into smaller modules
- See [docs/architecture/LARGE_FILE_REFACTORING.md](docs/architecture/LARGE_FILE_REFACTORING.md) for guidance

## TODO Policy

### Overview

All TODO comments must reference a GitHub issue to ensure technical debt is tracked and prioritized.

### Format

```python
# ✅ GOOD: References an issue
# TODO(#123): Implement caching for this endpoint

# ❌ BAD: No issue reference
# TODO: Implement caching
```

### Severity Levels

| Marker | Severity | Description | Issue Required |
|--------|----------|-------------|----------------|
| `FIXME` | CRITICAL | Broken code that needs immediate fix | ✅ Yes |
| `BUG` | CRITICAL | Known bug that needs fixing | ✅ Yes |
| `HACK` | HIGH | Temporary workaround that needs proper solution | ✅ Yes |
| `XXX` | HIGH | Problematic code that needs attention | ✅ Yes |
| `TODO` | MEDIUM | Planned improvement or feature | ⚠️ Recommended |
| `REFACTOR` | MEDIUM | Code that needs refactoring | ⚠️ Recommended |
| `OPTIMIZE` | LOW | Performance optimization opportunity | ❌ Optional |
| `NOTE` | LOW | Informational comment | ❌ Optional |

### Enforcement

- **Pre-commit hooks**: Block commits with CRITICAL/HIGH severity TODOs without issue references
- **CI/CD**: Fail builds if policy is violated
- **PR reviews**: Reviewers should check for compliant TODOs

### Creating Issues for TODOs

1. **Manual**:
   - Create a GitHub issue describing the work
   - Add appropriate labels: `technical-debt`, `todo`, severity label
   - Update the TODO comment with the issue number

2. **Automated** (for batch updates):
   ```bash
   # Generate TODO inventory
   python scripts/ci/scan_todos.py --format markdown --output TODO_INVENTORY.md

   # Create issues for TODOs (requires GitHub token)
   python scripts/ci/create_todo_issues.py --token $GITHUB_TOKEN --repo OmarA1-Bakri/ruleIQ --severity CRITICAL

   # Update TODO comments with issue references
   python scripts/ci/update_todo_references.py --mapping issues.json
   ```

### Exceptions

- **Documentation files** (README.md, CONTRIBUTING.md): TODOs allowed without issues
- **Example/template files**: TODOs allowed without issues
- **Test files**: TODOs allowed without issues (but discouraged)

### Best Practices

1. **Be specific**: Describe what needs to be done
   ```python
   # ✅ GOOD
   # TODO(#456): Replace mock data with API call to /api/v1/assessments

   # ❌ BAD
   # TODO: Fix this
   ```

2. **Include context**: Explain why the TODO exists
   ```python
   # TODO(#789): Implement retry logic for failed API calls
   # Currently fails silently, causing data loss in edge cases
   ```

3. **Link related TODOs**: If multiple TODOs are related, use the same issue
   ```python
   # TODO(#101): Part 1 - Extract provider layer
   # TODO(#101): Part 2 - Add unit tests for providers
   ```

4. **Clean up completed TODOs**: Remove TODO comments when work is done

### Quarterly Review

The team conducts quarterly TODO reviews:
- Review all open TODO-related issues
- Prioritize and schedule work
- Close obsolete TODOs
- Update severity levels if needed

## Testing Requirements

### Coverage Requirements

- **Minimum coverage**: 80% for new code
- **Target coverage**: 90%+
- **Critical paths**: 100% coverage required

### Running Tests

```bash
# Backend
pytest --cov=. --cov-report=html

# Frontend
cd frontend
pnpm test:coverage

# E2E
cd frontend
pnpm test:e2e
```

See [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) for detailed testing guidelines.

## Pull Request Process

### Before Submitting

1. ✅ All tests pass locally
2. ✅ Code follows style guidelines
3. ✅ No linter errors
4. ✅ Pre-commit hooks pass
5. ✅ TODOs reference issues (if applicable)
6. ✅ Documentation updated (if needed)
7. ✅ Changelog updated (for significant changes)

### PR Template

When creating a PR, include:

```markdown
## Description
[Brief description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Refactoring
- [ ] Documentation update
- [ ] Other (specify)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
- [ ] TODOs reference issues

## Related Issues
Closes #[issue number]
Related to #[issue number]
```

### Review Process

1. **Automated checks**: CI/CD must pass
2. **Code review**: At least one approval required
3. **Testing**: Reviewer should verify tests are adequate
4. **Documentation**: Reviewer should check docs are updated
5. **Merge**: Squash and merge (default) or rebase

## Security

### Reporting Vulnerabilities

Do **NOT** create public issues for security vulnerabilities. Instead:

1. Email: security@ruleiq.com (if available) or contact maintainers directly
2. Include: Description, impact, reproduction steps, suggested fix
3. Wait for response before public disclosure

### Security Best Practices

- **Never commit secrets**: Use environment variables or Doppler
- **Validate input**: Sanitize all user input
- **Use parameterized queries**: Prevent SQL injection
- **Keep dependencies updated**: Run `pip-audit` and `npm audit` regularly
- **Follow OWASP guidelines**: See [docs/security/](docs/security/)

See [docs/security/SECRET_HANDLING_GUIDE.md](docs/security/SECRET_HANDLING_GUIDE.md) for detailed security guidelines.

## Questions?

- **Documentation**: Check [docs/](docs/) directory
- **Issues**: Search [existing issues](https://github.com/OmarA1-Bakri/ruleIQ/issues)
- **Discussions**: Start a [discussion](https://github.com/OmarA1-Bakri/ruleIQ/discussions)
- **Chat**: Join our Slack channel (if available)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to RuleIQ!** 🎉
