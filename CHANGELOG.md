# Changelog

All notable changes to the Claude Agent Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.6.0] - 2026-02-03

### Added
- **Unified Repository Structure**: Consolidated agents, prompts, and governance from three separate locations into a single installable package
- **Installation System**: `install.sh` creates symlinks from `~/.claude/` to the repository
- **Snapshot/Rollback**: `snapshot.sh` and `rollback.sh` for version management
- **Package Manifest**: `manifest.yaml` tracks all component versions and dependencies
- **Configuration Templates**: Templates for `settings.json`, `settings.local.json`, `mcp_servers.json`
- **DevOps State Templates**: Initial templates for portfolio governance state

### Changed
- Prompts reorganized from `system-prompts-v2/` and `playbooks-v2/` into `prompts/system/` and `prompts/playbooks/`
- DevOps patterns moved from `~/.claude/devops/patterns/` to `patterns/`
- Knowledge base (`devlessons.md`) moved to `knowledge/`

### Migration Notes
- Run `./scripts/install.sh` to migrate from previous setup
- Previous configurations are backed up to `~/.claude-backup-YYYYMMDD-HHMMSS/`
- Local state (devops/, settings.local.json) is preserved

## [2.5.0] - 2026-01-31

### Added
- Worktree parallelization support
- BA can work ahead creating specs while coding agents implement in worktrees
- Feature backlog in manifest
- `worktree_manager.sh` helper script

## [2.0.0] - 2026-01-16

### Added
- Agentic development prompt pack v2
- Solution Designer agent
- Code Review agent (deep verification)
- QA Reviewer agent (quick governance check)
- Lessons Advisor agent
- DevOps Governor (macro agent)
- Persona lens packs

### Changed
- Reorganized from v3_atomic to v2.0 agentic model
- Split BA and coding into separate agents
- Added exclusive permissions model

## [1.0.0] - 2026-01-01

### Added
- Initial release
- Business Analyst system prompt
- Coding Agent system prompt
- Basic quality gates
