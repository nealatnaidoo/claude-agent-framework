# Operational Configuration

**Purpose**: Permissions, startup screen, and migration reference. Rarely needed during normal workflow.

---

## Permissions Configuration

Settings file: `~/.claude/settings.local.json`

### Two Permission Layers

1. **Bash Command Permissions** - which shell commands can execute
2. **Directory Access Permissions** - which paths Claude can read/write/create files in

Both must be configured for full access. See devlessons.md #28-29 for details.

### Auto-Allowed Commands (no prompts)
- **Testing**: pytest, npm test, bun test, ruff, mypy
- **Build**: npm run build, bun run build, docker build
- **Git (read)**: git status, git diff, git log, git branch, git fetch
- **Git (write)**: git add, git commit, git checkout, git stash, git pull
- **Package managers**: npm install, pip install, bun install, uv, poetry
- **Utilities**: ls, cat, head, tail, grep, find, curl, tree, mkdir, cp, mv
- **Deployment**: fly deploy, fly logs, docker compose, docker ps

### Directory Access (Write/Edit permissions)
- `~/Developer/**` - Full write/edit access to Developer folder
- `~/Documents/**` - Full write/edit access to Documents folder (legacy)

### Ask-First Commands (prompts before running)
- `git push` - Prompts before pushing to remote
- `npm publish` - Prompts before publishing packages
- `fly deploy --force` - Prompts before force deployments
- `docker push` - Prompts before pushing images
- `docker rm/rmi/stop` - Container destruction operations
- `git rebase` - History rewriting
- `psql/mysql/mongosh/redis-cli` - Database clients

### Denied Commands (never allowed)
- `Read(.env*)` - Prevents reading environment files with secrets
- `rm -rf` - Prevents dangerous recursive deletions
- `sudo rm` - Prevents privileged deletions
- `chmod 777` - Prevents insecure permissions

### Enabled Plugins
- `frontend-design@claude-plugins-official` - Production-grade UI components
- `github@claude-plugins-official` - GitHub integration
- `typescript-lsp@claude-plugins-official` - TypeScript language server
- `rust-analyzer-lsp@claude-plugins-official` - Rust language server

---

## Startup Screen & Status Command

A startup status screen automatically displays on the first prompt of each Claude Code session, showing:
- MCP server connection and available tools
- Available agents/subagents
- Credential status (API keys in Keychain)
- Service status (Docker, NotebookLM auth)
- Prime directives

### `/status` Command

When the user types `/status` or asks to "show status", run:
```bash
python3 ~/.claude/hooks/startup_check.py --force
```

The startup screen is triggered by a `UserPromptSubmit` hook in `~/.claude/settings.local.json`. The screen only shows once per terminal session (tracked via `~/.claude/.current_session`).

---

## Migrations

### Moving Development Folders

1. Run migration prompt: `migrations/MIGRATE_DEV_FOLDERS.md`
2. Update directory permissions in `~/.claude/settings.local.json`
3. Restart Claude Code session

### Migrating Project Artifacts to .claude/ Folder

For projects with legacy `{project}_spec.md` artifacts at root:

1. Run migration prompt: `migrations/MIGRATE_PROJECT_ARTIFACTS.md`
2. Or automated: `bash ~/.claude/scripts/migrate_to_claude_folder.sh {project_slug}`

---

## Technology Quick Reference

For technology-specific gotchas, consult `~/.claude/knowledge/devlessons.md`:

| Topic | Lessons |
|-------|---------|
| Databricks | 88-95 |
| MCP/Claude | 19-24, 30, 104 |
| React/Next.js | 18, 38-43, 59, 81, 85 |
| Fly.io | Section 3 |
| Risk Engine/Finance | 96, 97, 99 |

See `devlessons.md` lines 1209-1241 for "Top 30 Rules for Future Projects".

---

## Archive Information

Previous v3_atomic configuration archived at:
`~/Developer/claude-agent-framework/archive/v3_atomic_backup_2026-01-16/`

Rollback instructions: `~/Developer/claude-agent-framework/migrations/ROLLBACK_PROMPT.md`
