# Agent CLI Tools Architecture

## Overview

Agent CLI tools are utilities that agents invoke during their workflows. This document defines where tools live, how they're registered, and how agents reference them.

## Tool Categories

| Category | Location | Examples |
|----------|----------|----------|
| **Framework Scripts** | `scripts/` | validate_agents.py, worktree_manager.sh |
| **Packaged Tools** | External repos (PyPI/GitHub) | db-harness, future tools |
| **Pattern Generators** | `tools/generators/` | Project scaffolding, CI template generation |

## Directory Structure

```
claude-agent-framework/
├── scripts/                         # All CLI tools and scripts
│   ├── validate_agents.py           # Agent validation
│   ├── version_tracker.py           # Version tracking
│   ├── local_docker_validate.sh     # Pre-deploy Docker check
│   ├── worktree_manager.sh          # Git worktree helper
│   ├── dependency_graph.py          # Agent dependency visualization
│   ├── impact_analysis.py           # Change impact analysis
│   ├── new_agent.py                 # Create new agent from template
│   ├── install.sh                   # Framework installation
│   ├── migrate_to_claude_folder.sh  # Project migration helper
│   ├── rollback.sh                  # Framework rollback
│   ├── snapshot.sh                  # Create framework snapshot
│   └── uninstall.sh                 # Framework uninstall
│
├── tools/
│   └── registry.yaml                # Tool manifest (scripts + packages)
│
├── patterns/                        # CI/CD and architecture patterns
└── agents/                          # Agent prompts
```

## Tool Registry

All tools (internal and external) are registered in `tools/registry.yaml`:

```yaml
# tools/registry.yaml
schema_version: "1.0"
last_updated: "2026-02-04"

# Framework scripts (included in repo)
scripts:
  validate_agents:
    path: "scripts/validate_agents.py"
    description: "Validate agent prompts against schema"
    usage: "python scripts/validate_agents.py [agent.md]"
    used_by: [devops-governor, qa-reviewer]

  local_docker_validate:
    path: "scripts/local_docker_validate.sh"
    description: "Validate Docker build and health check locally"
    usage: "./scripts/local_docker_validate.sh --port 8080 --health /health"
    used_by: [devops-governor]
    decision_ref: "DEC-DEVOPS-006"

  worktree_manager:
    path: "scripts/worktree_manager.sh"
    description: "Manage git worktrees for parallel development"
    usage: "./scripts/worktree_manager.sh create|list|sync|remove"
    used_by: [business-analyst, backend-coding-agent, frontend-coding-agent]

  version_tracker:
    path: "scripts/version_tracker.py"
    description: "Track agent and artifact versions"
    usage: "python scripts/version_tracker.py scan|diff|history"
    used_by: [devops-governor]

# External packaged tools (installed separately)
packages:
  db-harness:
    repository: "https://github.com/nealatnaidoo/db-harness"
    version: "1.0.0"
    install: "pip install git+https://github.com/nealatnaidoo/db-harness.git@v1.0.0"
    description: "Database propagation, PII masking, schema drift detection"
    commands:
      - db-harness propagate
      - db-harness drift
      - db-harness consistency
      - db-harness detect-pii
      - db-harness audit
    used_by: [devops-governor]
    gates_implemented: [NN-DB-1, NN-DB-2, NN-DB-3, NN-DB-4]
    decision_refs: [DEC-DEVOPS-009, DEC-DEVOPS-014]

# Generators (included in repo)
generators:
  init_project:
    path: "tools/generators/init_project.py"
    description: "Initialize .claude/ folder structure for new projects"
    usage: "python tools/generators/init_project.py --slug myproject"
    creates:
      - ".claude/manifest.yaml"
      - ".claude/artifacts/"
      - ".claude/evidence/"
      - ".claude/evolution/"
      - ".claude/remediation/"

  generate_ci:
    path: "tools/generators/generate_ci.py"
    description: "Generate CI config from canonical templates"
    usage: "python tools/generators/generate_ci.py --template full-stack --platform gitlab"
    templates:
      - python-fastapi
      - nextjs-frontend
      - full-stack
      - azure-aks-python
      - azure-functions-python
      - databricks-jobs
```

## Installation

### Framework Tools

Included when you clone the framework:

```bash
# Clone framework
git clone https://github.com/nealatnaidoo/claude-agent-framework.git ~/.claude

# Scripts are immediately available
~/.claude/scripts/validate_agents.py
```

### External Packages

Install separately:

```bash
# db-harness
pip install git+https://github.com/nealatnaidoo/db-harness.git@v1.0.0

# Future tools would follow same pattern
pip install agent-tool-name
```

### All-in-One Installation Script

```bash
# tools/install_all.sh
#!/bin/bash

echo "Installing agent CLI tools..."

# Install Python packages
pip install git+https://github.com/nealatnaidoo/db-harness.git@v1.0.0

# Make scripts executable
chmod +x ~/.claude/scripts/*.sh

# Verify installation
echo "Verifying installations..."
db-harness --version
python ~/.claude/scripts/validate_agents.py --help

echo "Done. All tools installed."
```

## How Agents Reference Tools

### In Agent Prompts

```markdown
## Tools Available

This agent uses the following CLI tools:

| Tool | Command | Purpose |
|------|---------|---------|
| db-harness | `db-harness drift ...` | Schema drift detection |
| validate_agents | `python ~/.claude/scripts/validate_agents.py` | Agent validation |
```

### In DevOps Manifest

```yaml
tools:
  db_harness:
    version: "1.0.0"
    commands: [propagate, drift, consistency, detect-pii, audit]
    registry_ref: "tools/registry.yaml#packages.db-harness"
```

## When to Create a Separate Repo vs Script

| Criteria | Script (in framework) | Separate Repo |
|----------|----------------------|---------------|
| Lines of code | < 500 | > 500 |
| Dependencies | Minimal (stdlib only) | Has own deps |
| Reuse outside framework | No | Yes |
| Versioning needs | Follow framework | Independent |
| Testing requirements | Simple | Comprehensive |
| Documentation | README section | Full docs site |

### Examples

**Script (in framework):**
- `validate_agents.py` - ~200 lines, stdlib only, framework-specific
- `local_docker_validate.sh` - ~100 lines, bash only, framework-specific

**Separate repo:**
- `db-harness` - ~2000+ lines, has dependencies (typer, pydantic), reusable outside framework

## Tool Development Guidelines

### For Framework Scripts

1. Keep scripts focused (single purpose)
2. Use only stdlib where possible
3. Add to `tools/registry.yaml`
4. Document in script header
5. Add `used_by` in registry to track which agents use it

### For External Packages

1. Create separate repository
2. Use semantic versioning
3. Publish to PyPI when stable
4. Register in `tools/registry.yaml` with version
5. Add installation to `tools/install_all.sh`
6. Create DevOps decision record (DEC-DEVOPS-XXX)

## Future Tools Roadmap

| Tool | Category | Purpose | Status |
|------|----------|---------|--------|
| `agent-metrics` | Package | Collect agent performance metrics | Planned |
| `pattern-lint` | Script | Lint CI patterns for compliance | Planned |
| `project-audit` | Script | Full project Prime Directive audit | Planned |
| `secret-rotate` | Package | Credential rotation automation | Planned |
