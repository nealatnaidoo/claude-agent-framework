# Claude Agent Framework

A multi-agent governance framework for Claude Code. Provides structured workflows, validated agents with exclusive permissions, and mechanical enforcement via hooks — so your AI-assisted development is repeatable, auditable, and safe.

## What It Does

Instead of one monolithic AI session, this framework routes work through specialized agents:

| Agent | Purpose | Exclusive Permission |
|-------|---------|---------------------|
| **ops** | Portfolio-level CI/CD governance | Execute deployments |
| **persona** | Define user journeys | Define user journeys |
| **design** | Project inception, scope clarification | - |
| **ba** | Create specs, tasklists, quality gates | - |
| **back** | Python backend (hexagonal architecture) | Write backend code |
| **front** | React/TypeScript frontend (FSD) | Write frontend code |
| **qa** | Quick governance check (5-10 min) | - |
| **review** | Deep verification (60 min) | - |

Hooks enforce the rules mechanically — coding agents can't start without a spec, deployments require ops approval, and phase transitions are validated automatically.

## Prerequisites

- **Claude Code CLI** installed and working
- **Python 3.11+**
- **git**

## Quick Install

```bash
git clone https://github.com/YOUR_USERNAME/claude-agent-framework.git
cd claude-agent-framework
./bin/install.sh
```

The installer will:
1. Back up your existing `~/.claude/` configuration
2. Create symlinks from `~/.claude/` to the repository
3. Initialize local state directories
4. Copy config templates (if you don't have existing configs)
5. Install the `caf` CLI tool via pip

## API Key Setup

Set your Anthropic API key so Claude Code can find it:

```bash
# Works on all platforms (the default after install)
export ANTHROPIC_API_KEY=sk-ant-...

# Add to your shell profile to persist:
echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.zshrc  # or ~/.bashrc
```

**macOS users** can optionally use Keychain for secure storage:
```bash
# Store in Keychain
security add-generic-password -s "ANTHROPIC_API_KEY" -a "$USER" -w "sk-ant-..."

# Then edit ~/.claude/settings.json:
# Change "env:ANTHROPIC_API_KEY" to "keychain:ANTHROPIC_API_KEY"
```

## Your First 5 Minutes

After install, open Claude Code in any project directory:

1. **Status screen appears automatically** — the startup hook shows agent availability, credential status, and any warnings.

2. **Start a new governed project** — say "Initialize this project for governance" and the `init` agent scaffolds the `.claude/` folder with a manifest, artifact structure, and evolution log.

3. **Follow the agent lifecycle** — the framework guides you through: persona (user journeys) -> design (solution) -> BA (spec + tasklist) -> coding (back/front agents) -> QA -> review.

4. **For quick fixes**, say "Fast-track: fix the bug in X" — small changes skip the full lifecycle and go straight to coding -> QA.

## CLI Commands

Once installed, the `caf` CLI is available globally:

```bash
caf --help              # Show all commands
caf status              # Framework status
caf agents list         # List agents
caf agents validate     # Validate agent prompts
caf drift check         # Check architectural drift
caf cockpit portfolio   # Generate portfolio dashboard
caf lessons list        # Browse past lessons
```

## Directory Structure

```
claude-agent-framework/
├── agents/           # Agent prompt definitions
├── bin/              # Shell scripts (install, uninstall, snapshot, rollback)
├── commands/         # User-invocable slash commands
├── config/           # Configuration templates
├── docs/             # Governance documentation
├── hooks/            # Claude Code governance hooks
├── knowledge/        # Development lessons (devlessons.md)
├── patterns/         # CI/CD and architecture patterns
├── prompts/          # System prompts and playbooks
├── schemas/          # Validation schemas
├── skills/           # Skill definitions (drift, cockpit, etc.)
├── src/claude_cli/   # Python CLI tools
├── templates/        # Templates for new agents/artifacts
├── tests/            # CLI test suite
├── CLAUDE.md         # Global instructions (symlinked to ~/.claude/)
├── manifest.yaml     # Package manifest
├── pyproject.toml    # Python package definition
└── VERSION           # Current version
```

## Local Configuration (Not Tracked)

These files live in `~/.claude/` and are NOT symlinked — they're yours to customize:

- `settings.json` — API key helper
- `settings.local.json` — Permissions, hooks, and machine-specific paths
- `mcp_servers.json` — Your MCP server configuration
- `devops/` — Portfolio state, project registry, decision log

## Updating

Since the framework uses symlinks, pulling updates takes effect immediately:

```bash
cd <your-clone-path>
git pull
```

## Shell Scripts

```bash
./bin/snapshot.sh "before-big-change"   # Create a snapshot
./bin/rollback.sh --list                # List available snapshots
./bin/rollback.sh <snapshot-name>       # Rollback to snapshot
```

## Adding New Agents

```bash
caf agents new my-agent --type micro    # Interactive creation
# Or manually: cp templates/new_agent_template.md agents/my-agent.md
```

1. Edit the agent following `schemas/agent_prompt.schema.yaml`
2. Validate: `caf agents validate my-agent`
3. Update `manifest.yaml` with the new agent

## Uninstall

```bash
./bin/uninstall.sh
```

Removes symlinks but preserves your local state (devops/, configs, history).

## License

MIT
