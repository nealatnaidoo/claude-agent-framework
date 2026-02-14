---
name: commit
description: "Run tests, then create a conventional commit with test evidence"
user_invocable: true
---

# /commit — Test-Then-Commit Workflow

You are executing the `/commit` skill. Follow these steps exactly.

## Step 1: Detect Project Type

Determine the project type by checking for these files in the current directory (or parent dirs):

- `pyproject.toml` or `setup.py` → **Python project**
- `package.json` → **Node/TypeScript project**
- Both → **Full-stack project** (run both)

## Step 2: Run Tests

### Python Projects
```bash
pytest --tb=short -q
```

### Node/TypeScript Projects
```bash
npm run build && npm run lint
```

### Full-Stack Projects
Run both sets of checks.

**If any tests fail**: STOP. Report the failures and do NOT proceed to commit. Show the user what failed and suggest fixes.

## Step 3: Show Changes for Review

If tests pass, run:
```bash
git diff --stat
git diff --staged --stat
```

Show the user a summary of what will be committed. Include both staged and unstaged changes.

## Step 4: Stage Changes

Stage relevant changes. Prefer staging specific files by name rather than `git add -A`:
```bash
git add <specific-files>
```

Do NOT stage:
- `.env` files or credentials
- Large binary files
- Build artifacts (`node_modules/`, `__pycache__/`, `dist/`, `.next/`)

## Step 5: Generate Commit Message

Generate a **conventional commit** message based on the staged changes:

- Format: `type(scope): description`
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `style`, `perf`
- Keep the first line under 72 characters
- Add a body paragraph if the change is non-trivial

## Step 6: Create the Commit

```bash
git commit -m "$(cat <<'EOF'
type(scope): description

Optional body explaining why.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

## Step 7: Report

After committing, report:
- **Branch**: Current branch name
- **Files changed**: Count from the commit
- **Tests**: Count of tests that passed
- **Commit hash**: Short hash of the new commit

## Rules

- NEVER skip tests — the whole point is test-then-commit
- NEVER commit if tests fail
- NEVER use `git add -A` or `git add .` without reviewing what's staged
- NEVER push to remote (user must explicitly request that)
- ALWAYS include the Co-Authored-By trailer
- ALWAYS use conventional commit format
