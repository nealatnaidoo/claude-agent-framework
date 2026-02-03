# MCP Integration Strategy

**Version**: 1.0
**Date**: 2026-01-31
**Purpose**: Document how MCP servers integrate with the agent ecosystem

---

## Overview

MCP (Model Context Protocol) servers extend Claude Code's capabilities by providing specialized tools. They operate independently of the agent system but can be used by agents.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Claude Code                                      │
│                                                                          │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐        │
│   │    Agents     │     │   Built-in    │     │ MCP Servers   │        │
│   │ (Task tool)   │     │    Tools      │     │ (External)    │        │
│   └───────┬───────┘     └───────┬───────┘     └───────┬───────┘        │
│           │                     │                     │                  │
│           └─────────────────────┼─────────────────────┘                  │
│                                 │                                        │
│                                 ▼                                        │
│                    ┌─────────────────────┐                              │
│                    │  Tool Execution     │                              │
│                    │  (with permissions) │                              │
│                    └─────────────────────┘                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## MCP vs Agents

| Aspect | MCP Servers | Agents |
|--------|-------------|--------|
| Purpose | Provide tools | Orchestrate workflows |
| Scope | Single tool/capability | Multi-step processes |
| State | Stateless (per call) | Context-aware (per session) |
| Governance | Tool permissions | Agent operating model |
| Configuration | `~/.claude/mcp_servers.json` | Agent prompts |

---

## MCP Configuration

**Location**: `~/.claude/mcp_servers.json`

### Structure

```json
{
  "mcpServers": {
    "server-name": {
      "command": "/path/to/executable",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

### Environment Variables

MCP servers may need environment variables. Two approaches:

**1. Using `env` block (may not work in all cases):**
```json
{
  "server-name": {
    "command": "python",
    "args": ["-m", "my_mcp"],
    "env": {
      "MY_VAR": "/path/to/config"
    }
  }
}
```

**2. Using bash wrapper (more reliable):**
```json
{
  "server-name": {
    "command": "/bin/bash",
    "args": [
      "-c",
      "export MY_VAR=/path/to/config && python -m my_mcp"
    ]
  }
}
```

### Secrets from Keychain

For API keys stored in macOS Keychain:
```json
{
  "command": "/bin/bash",
  "args": [
    "-c",
    "export API_KEY=$(security find-generic-password -a $USER -s API_KEY_NAME -w) && python -m my_mcp"
  ]
}
```

---

## MCP Servers in Use

### Bureaucrat MCP

**Purpose**: BA artifact management, rules validation
**Location**: Python package `bureaucrat_mcp`
**Config Path**: `~/.claude/bureaucrat/rules.yaml`

```json
{
  "bureaucrat": {
    "command": "/bin/bash",
    "args": [
      "-c",
      "export BUREAUCRAT_MCP_RULES_PATH=/Users/naidooone/.claude/bureaucrat/rules.yaml && /Users/naidooone/.pyenv/shims/python -m bureaucrat_mcp"
    ]
  }
}
```

**Tools Provided**:
- Rule validation
- Artifact creation helpers
- Schema validation

---

## Integration with Agents

MCP tools are available to all agents but should be used according to agent permissions:

| Agent | Can Use MCP Tools For |
|-------|----------------------|
| `solution-designer` | Research, documentation |
| `business-analyst` | Artifact validation, schema checks |
| `coding-agent` | Code analysis, linting tools |
| `qa-reviewer` | Quality checks, security scanning |
| `devops-governor` | CI/CD validation, deployment tools |

**Restrictions Still Apply**:
- If an MCP tool could modify source code, only `coding-agent` should use it
- If an MCP tool could trigger deployment, only `devops-governor` should use it

---

## Adding New MCP Servers

1. Install the MCP server package
2. Create configuration file (if needed) in `~/.claude/`
3. Add entry to `~/.claude/mcp_servers.json`
4. Restart Claude Code
5. Verify with `/status` command

### Configuration File Location Convention

MCP server configs should be in `~/.claude/{server-name}/`:

```
~/.claude/
├── bureaucrat/
│   └── rules.yaml
├── future-mcp/
│   └── config.yaml
└── mcp_servers.json
```

---

## Troubleshooting

### Server Not Starting

1. Check logs: `~/.claude/logs/`
2. Verify command path exists
3. Test command manually in terminal
4. Check environment variables are exported

### Environment Variables Not Applied

If `env` block doesn't work, use bash wrapper approach (see above).

### Secrets Not Found

1. Verify Keychain item exists: `security find-generic-password -a $USER -s KEY_NAME`
2. Check exact key name matches
3. Ensure Keychain is unlocked

---

## Governance Notes

MCP servers are **tools**, not agents. They:
- Do NOT follow the manifest entry protocol
- Do NOT have identity tables
- Are NOT subject to agent restrictions directly

However, the **agents using MCP tools** must still follow their restrictions.

Example: If Bureaucrat MCP has a "write file" tool, only `coding-agent` should use it for source code.
