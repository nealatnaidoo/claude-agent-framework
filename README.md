# Claude Agent Framework

A multi-agent development ecosystem for Claude Code. Provides structured governance, validated agents, and systematic development workflows.

## Overview

This framework implements a portfolio of specialized agents that work together:

| Agent | Purpose | Exclusive Permission |
|-------|---------|---------------------|
| **ops** | Portfolio-level CI/CD governance | Execute deployments |
| **design** | Project inception, scope clarification | - |
| **ba** | Create specs, tasklists, rules | - |
| **coding-agent** | Implement code from BA specs | Write source code |
| **qa** | Quick governance check (5-10 min) | - |
| **review** | Deep verification (60 min) | - |
| **lessons** | Consult past lessons, improve gates | - |

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
chmod +x bin/install.sh
./bin/install.sh
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
├── bin/              # Shell scripts (install, snapshot, rollback)
├── commands/         # User-invocable slash commands
├── config/           # Configuration templates
├── data/             # CLI databases (DuckDB)
├── docs/             # Governance documentation
├── hooks/            # Claude Code hooks
├── knowledge/        # devlessons.md
├── lenses/           # Persona lens packs
├── patterns/         # CI/CD and architecture patterns
├── prompts/
│   ├── system/       # System prompts (methodology)
│   └── playbooks/    # Practical guides
├── schemas/          # Validation schemas
├── src/claude_cli/   # Python CLI tools
├── templates/        # Templates for new agents/artifacts
├── tests/            # CLI test suite
├── versions/         # Version tracking and snapshots
├── CLAUDE.md         # Global instructions
├── manifest.yaml     # Package manifest
├── pyproject.toml    # Python package definition
└── VERSION           # Current version
```

## Usage

### Install CLI Tools

```bash
cd ~/Developer/claude-agent-framework
pip install -e .
```

This installs the `caf` (Claude Agent Framework) CLI.

### CLI Commands

```bash
# Show help
caf --help

# Show framework status
caf status

# List agents
caf agents list

# Validate agents
caf agents validate
caf agents validate my-agent

# Create new agent
caf agents new my-agent --type micro

# Dependency analysis
caf analysis graph
caf analysis graph --mermaid
caf analysis impact my-agent
caf analysis impact my-agent --delete

# Version tracking
caf versions init
caf versions scan
caf versions query 2026-01-15
caf versions diff 2026-01-01 now

# Lessons management
caf lessons list
caf lessons search "testing"

# Worktree management
caf worktree list
caf worktree create feature-x
```

### Shell Scripts

```bash
# Create a snapshot
./bin/snapshot.sh "pre-major-change"

# Rollback to previous version
./bin/rollback.sh --list
./bin/rollback.sh 2026-02-03_v2.6.0_initial
```

### Update

```bash
cd ~/Developer/claude-agent-framework
git pull
```

Since the framework uses symlinks, updates are immediate.

### View Change History

```bash
# Full history
caf versions history

# Just agents
caf versions history --type agents
```

### Compare Two Points in Time

```bash
caf versions diff 2026-01-01 now
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

```bash
# Create agent interactively
caf agents new my-agent --type micro

# Or copy template manually
cp templates/new_agent_template.md agents/my-agent.md
```

1. Edit the agent following the schema in `schemas/agent_prompt.schema.yaml`
2. Run validation: `caf agents validate my-agent`
3. Update `manifest.yaml` with the new agent

## Versioning

The framework uses semantic versioning:

- **Major**: Breaking changes to agent interfaces or governance
- **Minor**: New agents, features, or patterns
- **Patch**: Bug fixes, documentation updates

Create snapshots before major changes:

```bash
./bin/snapshot.sh "before-new-agent"
```

## Uninstall

```bash
./bin/uninstall.sh
```

This removes symlinks but preserves your local state (devops/, configs, history).

## Contributing

1. Create a feature branch
2. Make changes
3. Run `caf agents validate` to verify
4. Update `manifest.yaml` versions as needed
5. Create a pull request

## License

MIT

## Acknowledgments

Built on lessons learned from 117+ development experiences. See `knowledge/devlessons.md`.
