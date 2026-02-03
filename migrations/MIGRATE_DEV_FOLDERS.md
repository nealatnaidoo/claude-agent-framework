# Development Folders Migration Prompt

**Purpose**: Update Claude Code permissions and related configurations when moving development folders to a new location.

**When to use**: Before or after moving your development projects from one directory to another (e.g., `~/Documents` → `~/code`).

---

## Instructions

Copy the prompt below and paste it into a new Claude Code session. Fill in the OLD_PATH and NEW_PATH values.

---

## Migration Prompt

```
I am migrating my development folders from one location to another. Please help me update all path-specific configurations.

OLD_PATH: /Users/naidooone/Documents
NEW_PATH: [FILL IN NEW PATH, e.g., /Users/naidooone/code]

Please perform the following migration tasks:

## 1. Audit Current Path References

Read and analyze these files for path-specific settings:

1. `~/.claude/settings.local.json` - Global Claude Code permissions
2. `~/.claude/CLAUDE.md` - Global instructions (check for hardcoded paths)
3. `~/Documents/development prompts/devlessons.md` - Check for path references

For each file, list all occurrences of the OLD_PATH.

## 2. Show Proposed Changes

For each path reference found, show:
- File location
- Current value
- Proposed new value
- Risk assessment (safe/review/skip)

Format as a table:
| File | Current Path | New Path | Risk |
|------|--------------|----------|------|

## 3. Ask for Confirmation

Before making changes, ask me to confirm:
- Which changes to apply
- Which to skip
- Any custom modifications needed

## 4. Apply Changes

After confirmation, update each file and show the diff.

## 5. Additional Checks

After updating configs, also check:
- Any project-level `.claude/settings.json` files in OLD_PATH that need moving
- Any symlinks that might break
- Git remote URLs (shouldn't change, but verify)

## 6. Verification

After migration:
1. Show the updated permissions summary
2. Confirm the new paths are correctly configured
3. Remind me to restart Claude Code session

## Expected Permission Updates

These permission types commonly need path updates:
- `Write(path/**)`
- `Edit(path/**)`
- `Read(path/**)`
- `WebFetch(domain:...)` - usually don't need changes

## Safety Notes

- Do NOT update system paths (/etc, /usr, /System)
- Do NOT update paths to external services
- PRESERVE deny rules exactly as-is
- Keep backup of settings before changes
```

---

## Quick Reference: Current Path-Specific Permissions

As of 2026-01-17, these paths are configured in `~/.claude/settings.local.json`:

```
Write(~/Documents/**)
Write(/Users/naidooone/Documents/**)
Edit(~/Documents/**)
Edit(/Users/naidooone/Documents/**)
```

---

## Post-Migration Checklist

After running the migration prompt:

- [ ] Verify new paths work: create a test file in new location
- [ ] Restart Claude Code session
- [ ] Test a Write operation in the new directory
- [ ] Test an Edit operation in the new directory
- [ ] Remove old path permissions (optional, for cleanliness)
- [ ] Update CLAUDE.md if it references old paths
- [ ] Move any project-level `.claude/` folders

---

## Rollback

If something goes wrong, restore from backup:

```bash
# Before migration, create backup
cp ~/.claude/settings.local.json ~/.claude/settings.local.json.backup

# To rollback
cp ~/.claude/settings.local.json.backup ~/.claude/settings.local.json
```

---

## Related Lessons

- devlessons.md #28: Claude Code Permissions Configuration
- devlessons.md #29: Claude Code Directory Access Permissions
