# Pre-Unification Archive

**Date**: 2026-02-03
**Reason**: Consolidated three locations into unified `claude-agent-framework` repository

## Archived Items

### 1. ~/.claude/.git (claude-dot-git/)

The git history from the original `~/.claude/` directory before it was converted to symlinks.

### 2. ~/Developer/claude/prompts/ (prompts-repo-info.txt)

Git log and remote info for the original prompts repository. The actual repository still exists at `~/Developer/claude/prompts/` and can be:
- Deleted if no longer needed
- Kept as historical reference
- Used to push to a separate "prompts-only" remote if desired

### 3. ~/.dotfiles/claude/.claude/ (dotfiles-info.txt)

Info about the dotfiles symlink setup. The dotfiles still contain:
- `settings.json` - still active via symlink
- `settings.local.json` - still active via symlink
- `mcp_servers.json` - still active via symlink

These can continue to work OR you can move them to `~/.claude/` directly.

## Current Setup

After unification, `~/.claude/` contains:
- **Symlinks** to `~/Developer/claude-agent-framework/`:
  - agents/, prompts/, schemas/, docs/, lenses/, patterns/, templates/, commands/, hooks/, scripts/, knowledge/, CLAUDE.md
- **Local state** (not symlinked):
  - devops/ (your portfolio state with 16 decisions)
  - settings*.json, mcp_servers.json (via dotfiles symlinks)
  - Runtime directories (history, cache, plugins, etc.)

## Cleanup Actions (Optional)

Once you've verified the new setup works:

```bash
# Remove old prompts repo (content is now in claude-agent-framework)
rm -rf ~/Developer/claude/prompts/

# Update dotfiles to point to new location (or remove)
# Option A: Update symlinks in dotfiles to point to new repo
# Option B: Remove dotfiles symlinks and keep files directly in ~/.claude/
```

## Rollback

If you need to restore the old setup:

1. Uninstall: `~/Developer/claude-agent-framework/scripts/uninstall.sh`
2. Restore from backup: `cp -r ~/.claude-backup-20260203-224706/* ~/.claude/`
3. The old git history is in `archive/pre-unification-2026-02-03/claude-dot-git/`
