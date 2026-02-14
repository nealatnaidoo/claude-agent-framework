# CLAUDE.md Change Protocol

**Version**: 1.0
**Date**: 2026-01-31
**Purpose**: Governance for modifications to global CLAUDE.md and agent configuration

---

## Overview

The global `~/.claude/CLAUDE.md` file is the central configuration that all Claude Code sessions read. Changes to this file affect:
- All projects using Claude Code
- All agent behaviors and references
- Document locations and conventions
- Quality gates and compliance requirements

**Changes must be controlled** to prevent contamination of the agent ecosystem.

---

## Change Classification

### Level 1: Cosmetic (Low Risk)
- Typo fixes
- Formatting improvements
- Clarifying existing text
- Adding examples to existing sections

**Protocol**: Direct edit, no validation required

### Level 2: Documentation (Medium Risk)
- Adding new reference links
- Updating version numbers
- Adding new lessons references
- Updating file paths that don't affect agents

**Protocol**:
1. Run validation script before
2. Make change
3. Run validation script after
4. Verify no agent breakage

### Level 3: Structural (High Risk)
- Adding/removing sections
- Changing document location conventions
- Modifying agent references
- Updating compliance requirements
- Changing folder structure conventions

**Protocol**: Full change protocol (see below)

### Level 4: Agent Model (Critical)
- Changing internal/visiting agent model
- Modifying manifest schema
- Changing ID sequencing rules
- Modifying entry/startup protocols
- Changing output location conventions

**Protocol**: Full change protocol + agent updates required

---

## Full Change Protocol

### Pre-Change Checklist

```
[ ] 1. Document the reason for change
[ ] 2. Identify change level (1-4)
[ ] 3. List all affected files
[ ] 4. Run validation script: python ~/.claude/scripts/validate_agents.py
[ ] 5. All agents pass validation
[ ] 6. Create backup of current state
```

### Change Execution

```
[ ] 7. Update affected agent prompts FIRST (if Level 3-4)
[ ] 8. Update CLAUDE.md
[ ] 9. Update any affected schema files
[ ] 10. Update any affected template files
[ ] 11. Run validation script again
[ ] 12. All agents still pass validation
```

### Post-Change Verification

```
[ ] 13. Test one internal agent manually
[ ] 14. Test one visiting agent manually (if applicable)
[ ] 15. Update version number in CLAUDE.md header
[ ] 16. Document change in change log
```

---

## Files That Require This Protocol

| File | Change Level | Notes |
|------|-------------|-------|
| `~/.claude/CLAUDE.md` | 2-4 | Global instructions |
| `~/.claude/agents/*.md` | 3-4 | Agent prompts |
| `~/.claude/schemas/*.yaml` | 4 | Validation schemas |
| `~/.claude/templates/*.md` | 3 | Agent templates |
| `~/.claude/docs/agent_operating_model.md` | 3-4 | Operating model |
| `~/.claude/docs/document_consistency.md` | 3 | Document locations |
| `~/.claude/docs/agent_creation_guide.md` | 3-4 | Agent creation |

---

## Affected Files Matrix

When changing these CLAUDE.md sections, these files may need updates:

### Document Locations Section

| If you change... | Update these files |
|------------------|-------------------|
| Artifact folder convention | All agent prompts, document_consistency.md, agent_creation_guide.md |
| Evidence folder convention | All agent prompts, manifest schema |
| Remediation folder convention | QA/Code Review agents, manifest schema |
| Naming conventions | BA agent, all review agents |

### Agent References Section

| If you change... | Update these files |
|------------------|-------------------|
| Agent names | All agents listed |
| Agent descriptions | Agent prompts, Task tool references |
| Agent tool allowlists | Agent prompts |
| Agent model assignments | Agent prompts |

### Compliance Section

| If you change... | Update these files |
|------------------|-------------------|
| Prime Directive | All agent prompts, agent_operating_model.md |
| Hexagonal rules | Coding agent, QA agent, Code Review agent |
| Determinism rules | Coding agent, QA agent |
| Testing requirements | All agents that verify tests |

### Manifest Section

| If you change... | Update these files |
|------------------|-------------------|
| Manifest location | All agent prompts |
| Manifest schema | manifest.schema.yaml, all agents |
| Required sections | All agents that read/write manifest |

---

## Validation Script Usage

### Before Any Change

```bash
# Validate all agents
python ~/.claude/scripts/validate_agents.py

# Expected output: ALL PASSED
```

### After Any Change

```bash
# Validate all agents again
python ~/.claude/scripts/validate_agents.py

# If any FAIL, revert changes and fix agents first
```

### Validate Specific Agent

```bash
# After updating a specific agent
python ~/.claude/scripts/validate_agents.py design.md
```

---

## Change Log Template

Maintain a change log at the top of CLAUDE.md or in a separate file:

```markdown
## Change Log

### v2.4 - 2026-02-01
**Level**: 3 (Structural)
**Reason**: Added new security auditor agent
**Files Changed**:
- ~/.claude/agents/security-auditor.md (new)
- ~/.claude/CLAUDE.md (added to agent table)
**Validation**: All agents pass
**Tested**: Manually verified security-auditor startup

### v2.3 - 2026-01-31
**Level**: 4 (Agent Model)
**Reason**: Implemented agent operating model with internal/visiting distinction
**Files Changed**:
- ~/.claude/CLAUDE.md
- ~/.claude/agents/*.md (all)
- ~/.claude/schemas/project_manifest.schema.yaml
- ~/.claude/docs/agent_operating_model.md (new)
**Validation**: All agents pass
**Tested**: Verified internal and visiting agent behavior
```

---

## Emergency Rollback

If changes break agents:

### Quick Rollback

```bash
# If you made backups
cp ~/.claude/CLAUDE.md.backup ~/.claude/CLAUDE.md

# Or revert from git if tracked
cd ~/.claude && git checkout CLAUDE.md
```

### Identify Breaking Change

```bash
# Run validation with verbose output
python ~/.claude/scripts/validate_agents.py --verbose

# Check specific failing agent
python ~/.claude/scripts/validate_agents.py failing-agent.md --verbose
```

---

## Prohibited Changes

These changes are **NEVER** allowed without full ecosystem review:

| Change | Why Prohibited |
|--------|---------------|
| Remove manifest requirement | Breaks all agent entry protocols |
| Change `.claude/` folder name | Breaks all path references |
| Remove identity section requirement | Agents lose permission awareness |
| Change ID sequencing rules | Creates duplicate/conflicting IDs |
| Remove Prime Directive | Breaks compliance model |

---

## Version Numbering

CLAUDE.md uses semantic versioning in its header:

```
**Version**: v{major}.{minor}
```

| Change Level | Version Bump |
|-------------|--------------|
| Level 1 (Cosmetic) | No change |
| Level 2 (Documentation) | Minor (+0.1) |
| Level 3 (Structural) | Minor (+0.1) |
| Level 4 (Agent Model) | Major (+1.0) |

---

## Contacts and Escalation

For questions about this protocol:
1. Review `~/.claude/docs/agent_operating_model.md`
2. Check `~/.claude/docs/agent_creation_guide.md`
3. Run validation script for specific guidance

---

## Quick Reference

| Need | Command/File |
|------|-------------|
| Validate all agents | `python ~/.claude/scripts/validate_agents.py` |
| Agent creation guide | `~/.claude/docs/agent_creation_guide.md` |
| Agent template | `~/.claude/templates/new_agent_template.md` |
| Operating model | `~/.claude/docs/agent_operating_model.md` |
| Manifest schema | `~/.claude/schemas/project_manifest.schema.yaml` |
| Agent prompt schema | `~/.claude/schemas/agent_prompt.schema.yaml` |
