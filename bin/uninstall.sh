#!/bin/bash
# Claude Agent Framework Uninstaller
# Removes symlinks from ~/.claude/ (preserves local state)

set -e

TARGET_DIR="$HOME/.claude"

echo "============================================"
echo "Claude Agent Framework Uninstaller"
echo "============================================"
echo ""

# Content directories that are symlinked
CONTENT_DIRS=(agents prompts schemas docs lenses patterns templates commands hooks scripts knowledge)

echo "This will remove the following symlinks from ~/.claude/:"
for dir in "${CONTENT_DIRS[@]}"; do
    if [ -L "$TARGET_DIR/$dir" ]; then
        echo "  - $dir -> $(readlink "$TARGET_DIR/$dir")"
    fi
done
if [ -L "$TARGET_DIR/CLAUDE.md" ]; then
    echo "  - CLAUDE.md -> $(readlink "$TARGET_DIR/CLAUDE.md")"
fi

echo ""
echo "The following will be PRESERVED:"
echo "  - devops/ (your portfolio state)"
echo "  - settings.json, settings.local.json, mcp_servers.json"
echo "  - history.jsonl, cache/, and other runtime data"
echo ""

read -p "Continue with uninstall? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo "Removing symlinks..."

for dir in "${CONTENT_DIRS[@]}"; do
    if [ -L "$TARGET_DIR/$dir" ]; then
        rm "$TARGET_DIR/$dir"
        echo "  Removed: $dir"
    fi
done

if [ -L "$TARGET_DIR/CLAUDE.md" ]; then
    rm "$TARGET_DIR/CLAUDE.md"
    echo "  Removed: CLAUDE.md"
fi

echo ""
echo "============================================"
echo "Uninstall complete"
echo "============================================"
echo ""
echo "Your local state in ~/.claude/ has been preserved."
echo "To fully remove, manually delete ~/.claude/"
echo ""
echo "To reinstall, run: ./bin/install.sh"
