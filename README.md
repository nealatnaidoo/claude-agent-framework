# Claude Agent Framework

A governance layer for Claude Code that replaces one big AI conversation with a team of specialized agents, each with strict permissions. Instead of hoping the AI does the right thing, hooks mechanically enforce it — coding can't start without a spec, deployments need ops approval, and every change is traceable.

## What It Does

You describe what you want, and the framework routes it through agents:

```
You: "I want to build a task manager app"
                  |
            init agent         scaffolds project, registers in portfolio
                  |
           persona agent       defines user journeys
                  |
           design agent        bounded solution (consults ops)
                  |
             ba agent          writes spec, tasklist, quality rules
                  |
       back + front agents     implement code (only from the spec)
                  |
            qa agent           governance check after each task
                  |
           review agent        deep verification after feature
```

For small fixes, a **fast-track path** skips the ceremony: coding -> QA -> done.

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

**Exclusive permissions** mean the backend agent literally cannot write frontend code, and vice versa. The ops agent is the only one that can deploy. This isn't a suggestion — hooks block the action if the wrong agent tries.

**9 governance hooks** fire automatically on tool use and agent startup. They check: Does a spec exist? Is the phase correct? Is this agent allowed to do this? No human has to remember to check.

## What You Get Out of the Box

| Capability | How |
|---|---|
| 12 specialized agents | Each with defined scope and permissions |
| 9 governance hooks | Block unauthorized actions mechanically |
| CLI tooling (`caf`) | Status, drift detection, validation, dashboards |
| Portfolio cockpit | HTML dashboard aggregating all governed projects |
| Architectural drift detection | Verify decisions are reflected in code |
| Batch processing | Run parallel headless agent jobs |
| Lesson system | 117+ development lessons indexed by topic |
| Snapshot/rollback | Point-in-time recovery for the framework itself |

---

## New User Setup

### Prerequisites

- **Claude Code CLI** — [install instructions](https://docs.anthropic.com/en/docs/claude-code/overview)
- **Python 3.11+** — check with `python3 --version`
- **git**

### Install

```bash
git clone https://github.com/nealatnaidoo/claude-agent-framework.git
cd claude-agent-framework
./bin/install.sh
```

That's it. The installer will:
- Back up your existing `~/.claude/` if you have one
- Symlink the framework into `~/.claude/`
- Install the `caf` CLI tool
- Copy config templates
- Display a full welcome guide explaining what was installed

Open Claude Code in any project directory and you're ready to go. The framework uses whatever auth Claude Code already has — no extra API key needed.

> **Custom API key (optional):** If you need a separate key for direct API access, set `export ANTHROPIC_API_KEY=sk-ant-...` and add `{"apiKeyHelper": "env:ANTHROPIC_API_KEY"}` to `~/.claude/settings.json`.

---

## Your First 5 Minutes

1. **Status screen appears automatically** — the startup hook shows agent availability, credential status, and any warnings.

2. **Start a governed project** — say "Initialize this project for governance" and the `init` agent scaffolds the `.claude/` folder with manifest, evolution log, and registers the project in your portfolio.

3. **Follow the agent lifecycle** — the framework guides you through: persona (user journeys) -> design (solution) -> BA (spec + tasklist) -> coding (back/front agents) -> QA -> review.

4. **For quick fixes**, say "Fast-track: fix the bug in X" — small changes skip the full lifecycle and go straight to coding -> QA.

5. **See the big picture** — run `caf cockpit portfolio` at any time to see where all your projects stand.

---

## CLI Quick Reference

```bash
caf --help              # Show all commands
caf status              # Framework status
caf agents list         # List agents
caf agents validate     # Validate agent prompts
caf drift check         # Check architectural drift
caf cockpit project     # Project dashboard
caf cockpit portfolio   # Portfolio dashboard
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
├── hooks/            # Claude Code governance hooks (9 scripts)
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
