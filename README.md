# Claude Agent Framework

A multi-agent development ecosystem for Claude Code. Provides structured governance, validated agents, and systematic development workflows.

## Overview

This framework implements a portfolio of specialized agents that work together:

| Agent | Purpose | Exclusive Permission |
|-------|---------|---------------------|
| **devops-governor** | Portfolio-level CI/CD governance | Execute deployments |
| **solution-designer** | Project inception, scope clarification | - |
| **business-analyst** | Create specs, tasklists, rules | - |
| **coding-agent** | Implement code from BA specs | Write source code |
| **qa-reviewer** | Quick governance check (5-10 min) | - |
| **code-review-agent** | Deep verification (60 min) | - |
| **lessons-advisor** | Consult past lessons, improve gates | - |

## Installation

### Prerequisites

- Claude Code CLI installed
- Python 3.10+
- macOS or Linux

### Quick Install

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/claude-agent-framework.git ~/Developer/claude-agent-framework

# Run the installer
cd ~/Developer/claude-agent-framework
chmod +x scripts/install.sh
./scripts/install.sh
```

The installer will:
1. Back up your existing `~/.claude/` configuration
2. Create symlinks from `~/.claude/` to the repository
3. Initialize local state directories (devops/, etc.)
4. Copy config templates if you don't have existing configs

### Manual Installation

If you prefer manual setup:

```bash
# Create symlinks
ln -s ~/Developer/claude-agent-framework/agents ~/.claude/agents
ln -s ~/Developer/claude-agent-framework/prompts ~/.claude/prompts
ln -s ~/Developer/claude-agent-framework/schemas ~/.claude/schemas
ln -s ~/Developer/claude-agent-framework/docs ~/.claude/docs
# ... etc for other directories

ln -s ~/Developer/claude-agent-framework/CLAUDE.md ~/.claude/CLAUDE.md
```

## Directory Structure

```
claude-agent-framework/
├── agents/           # Agent prompt definitions
├── prompts/
│   ├── system/      # System prompts (methodology)
│   └── playbooks/   # Practical guides
├── schemas/         # Validation schemas
├── docs/            # Governance documentation
├── lenses/          # Persona lens packs
├── patterns/        # CI/CD and architecture patterns
├── templates/       # Templates for new agents/artifacts
├── commands/        # User-invocable commands
├── hooks/           # Claude Code hooks
├── scripts/         # Tooling (install, validate, snapshot)
├── knowledge/       # devlessons.md
├── config/          # Configuration templates
├── versions/        # Version tracking and snapshots
├── CLAUDE.md        # Global instructions
├── manifest.yaml    # Package manifest
└── VERSION          # Current version
```

## Usage

### Validate Agents

```bash
python3 ~/.claude/scripts/validate_agents.py
```

### Create a Snapshot

```bash
./scripts/snapshot.sh "pre-major-change"
```

### Rollback to Previous Version

```bash
# List available snapshots
./scripts/rollback.sh --list

# Rollback
./scripts/rollback.sh 2026-02-03_v2.6.0_initial
```

### Update

```bash
cd ~/Developer/claude-agent-framework
git pull
```

Since the framework uses symlinks, updates are immediate.

## Bi-Temporal Version Tracking

The framework tracks all component changes with two time dimensions:
- **Valid time**: When a version was active
- **Transaction time**: When the change was recorded

### Initialize Tracking

```bash
python3 scripts/version_tracker.py init
```

### Scan for Changes

```bash
# Show what would be recorded
python3 scripts/version_tracker.py scan --dry-run

# Record changes
python3 scripts/version_tracker.py scan
```

### Query Historical State

```bash
# What was the system like on a specific date?
python3 scripts/version_tracker.py query 2026-01-15

# Current state
python3 scripts/version_tracker.py query now
```

### View Change History

```bash
# Full history
python3 scripts/version_tracker.py history

# Just agents
python3 scripts/version_tracker.py history --type agents
```

### Compare Two Points in Time

```bash
python3 scripts/version_tracker.py diff 2026-01-01 now
```

### Automatic Tracking (Optional)

Install the pre-commit hook to auto-record changes:

```bash
cp hooks/pre-commit-version-track .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Customization

### Local Configuration (not tracked)

These files live in `~/.claude/` and are NOT symlinked:

- `settings.local.json` - Machine-specific paths and permissions
- `mcp_servers.json` - Your MCP server configuration
- `devops/manifest.yaml` - Your portfolio state
- `devops/project_registry.yaml` - Your registered projects
- `devops/decisions.md` - Your decision log

### Adding New Agents

1. Copy the template: `cp templates/new_agent_template.md agents/my-agent.md`
2. Edit the agent following the schema in `schemas/agent_prompt.schema.yaml`
3. Run validation: `python3 scripts/validate_agents.py agents/my-agent.md`
4. Update `manifest.yaml` with the new agent

## Versioning

The framework uses semantic versioning:

- **Major**: Breaking changes to agent interfaces or governance
- **Minor**: New agents, features, or patterns
- **Patch**: Bug fixes, documentation updates

Create snapshots before major changes:

```bash
./scripts/snapshot.sh "before-new-agent"
```

## Uninstall

```bash
./scripts/uninstall.sh
```

This removes symlinks but preserves your local state (devops/, configs, history).

## Contributing

1. Create a feature branch
2. Make changes
3. Run `python3 scripts/validate_agents.py` to verify
4. Update `manifest.yaml` versions as needed
5. Create a pull request

## License

MIT

## Acknowledgments

Built on lessons learned from 117+ development experiences. See `knowledge/devlessons.md`.
