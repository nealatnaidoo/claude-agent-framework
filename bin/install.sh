#!/bin/bash
# Claude Agent Framework Installer
# Creates symlinks from ~/.claude/ to the repository

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET_DIR="$HOME/.claude"
BACKUP_DIR="$HOME/.claude-backup-$(date +%Y%m%d-%H%M%S)"

echo "============================================"
echo "Claude Agent Framework Installer"
echo "============================================"
echo ""
echo "Repository: $REPO_DIR"
echo "Target:     $TARGET_DIR"
echo ""

# Check if running from correct location
if [ ! -f "$REPO_DIR/VERSION" ]; then
    echo "ERROR: VERSION file not found. Are you running from the correct directory?"
    exit 1
fi

VERSION=$(cat "$REPO_DIR/VERSION")
echo "Installing version: $VERSION"
echo ""

# Confirm installation
read -p "This will create symlinks in ~/.claude/. Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# 1. Backup existing ~/.claude if it has content (not just symlinks)
if [ -d "$TARGET_DIR" ]; then
    # Check if there are any non-symlink files/dirs that might need backup
    REAL_CONTENT=$(find "$TARGET_DIR" -maxdepth 1 -type f -o -type d ! -name ".*" 2>/dev/null | head -5)
    if [ -n "$REAL_CONTENT" ]; then
        echo ""
        echo "Backing up existing ~/.claude to $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"

        # Copy local state files (not symlinks)
        for item in devops settings.json settings.local.json mcp_servers.json history.jsonl; do
            if [ -e "$TARGET_DIR/$item" ] && [ ! -L "$TARGET_DIR/$item" ]; then
                cp -r "$TARGET_DIR/$item" "$BACKUP_DIR/" 2>/dev/null || true
            fi
        done

        # Backup .git if exists (we're archiving the old repo)
        if [ -d "$TARGET_DIR/.git" ]; then
            cp -r "$TARGET_DIR/.git" "$BACKUP_DIR/"
        fi

        echo "Backup created at: $BACKUP_DIR"
    fi
fi

# 2. Create target directory if needed
mkdir -p "$TARGET_DIR"

# 3. Remove old symlinks that point elsewhere
echo ""
echo "Cleaning up old symlinks..."
CONTENT_DIRS=(agents prompts schemas docs lenses patterns templates commands hooks scripts knowledge)
for dir in "${CONTENT_DIRS[@]}"; do
    if [ -L "$TARGET_DIR/$dir" ]; then
        rm "$TARGET_DIR/$dir"
        echo "  Removed old symlink: $dir"
    fi
done

if [ -L "$TARGET_DIR/CLAUDE.md" ]; then
    rm "$TARGET_DIR/CLAUDE.md"
    echo "  Removed old symlink: CLAUDE.md"
fi

# 4. Create new symlinks for CONTENT directories
echo ""
echo "Creating symlinks..."
for dir in "${CONTENT_DIRS[@]}"; do
    if [ -d "$TARGET_DIR/$dir" ] && [ ! -L "$TARGET_DIR/$dir" ]; then
        echo "  WARNING: $TARGET_DIR/$dir exists and is a real directory."
        echo "           Moving to backup and creating symlink."
        mv "$TARGET_DIR/$dir" "$BACKUP_DIR/$dir-real" 2>/dev/null || true
    fi

    if [ -d "$REPO_DIR/$dir" ]; then
        ln -s "$REPO_DIR/$dir" "$TARGET_DIR/$dir"
        echo "  Linked: $dir -> $REPO_DIR/$dir"
    fi
done

# 5. Symlink CLAUDE.md
ln -s "$REPO_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md"
echo "  Linked: CLAUDE.md"

# 6. Initialize LOCAL directories (don't overwrite existing)
echo ""
echo "Initializing local state directories..."

if [ ! -d "$TARGET_DIR/devops" ]; then
    mkdir -p "$TARGET_DIR/devops"
    if [ -d "$REPO_DIR/config/init/devops" ]; then
        cp -r "$REPO_DIR/config/init/devops/"* "$TARGET_DIR/devops/"
        echo "  Initialized: devops/ (from templates)"
    fi
else
    echo "  Keeping existing: devops/"
fi

# 7. Copy config templates if not exist
echo ""
echo "Setting up configuration files..."

if [ ! -f "$TARGET_DIR/settings.json" ]; then
    if [ -f "$REPO_DIR/config/settings.json.template" ]; then
        cp "$REPO_DIR/config/settings.json.template" "$TARGET_DIR/settings.json"
        echo "  Created: settings.json (from template - customize as needed)"
    fi
else
    echo "  Keeping existing: settings.json"
fi

if [ ! -f "$TARGET_DIR/settings.local.json" ]; then
    if [ -f "$REPO_DIR/config/settings.local.json.template" ]; then
        cp "$REPO_DIR/config/settings.local.json.template" "$TARGET_DIR/settings.local.json"
        echo "  Created: settings.local.json (from template - customize as needed)"
    fi
else
    echo "  Keeping existing: settings.local.json"
fi

if [ ! -f "$TARGET_DIR/mcp_servers.json" ]; then
    if [ -f "$REPO_DIR/config/mcp_servers.json.template" ]; then
        cp "$REPO_DIR/config/mcp_servers.json.template" "$TARGET_DIR/mcp_servers.json"
        echo "  Created: mcp_servers.json (from template - customize as needed)"
    fi
else
    echo "  Keeping existing: mcp_servers.json"
fi

# 8. Create runtime directories if needed
echo ""
echo "Ensuring runtime directories exist..."
RUNTIME_DIRS=(cache debug downloads file-history paste-cache plans plugins projects session-env shell-snapshots tasks telemetry todos)
for dir in "${RUNTIME_DIRS[@]}"; do
    mkdir -p "$TARGET_DIR/$dir"
done
echo "  Runtime directories ready"

# 8.5. Install Python CLI tools
echo ""
echo "Installing CLI tools..."
if command -v pip3 &> /dev/null; then
    pip3 install -e "$REPO_DIR" 2>&1 | tail -1 || echo "  WARNING: pip install failed. Run manually: pip3 install -e $REPO_DIR"
elif command -v pip &> /dev/null; then
    pip install -e "$REPO_DIR" 2>&1 | tail -1 || echo "  WARNING: pip install failed. Run manually: pip install -e $REPO_DIR"
else
    echo "  WARNING: pip not found. Install Python CLI tools manually: pip install -e $REPO_DIR"
fi

# 9. Verify installation
echo ""
echo "============================================"
echo "Verifying installation..."
echo "============================================"

ERRORS=0

# Check symlinks
for dir in "${CONTENT_DIRS[@]}"; do
    if [ -L "$TARGET_DIR/$dir" ]; then
        echo "  [OK] $dir"
    else
        echo "  [FAIL] $dir - symlink not created"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ -L "$TARGET_DIR/CLAUDE.md" ]; then
    echo "  [OK] CLAUDE.md"
else
    echo "  [FAIL] CLAUDE.md - symlink not created"
    ERRORS=$((ERRORS + 1))
fi

# Check local directories
if [ -d "$TARGET_DIR/devops" ]; then
    echo "  [OK] devops/ (local state)"
else
    echo "  [FAIL] devops/ - not created"
    ERRORS=$((ERRORS + 1))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "============================================"
    echo "Installation complete! Version $VERSION"
    echo "============================================"
    echo ""
    echo "Next steps:"
    echo "1. Set your API key: export ANTHROPIC_API_KEY=sk-ant-..."
    echo "   (macOS users can optionally use keychain — see README)"
    echo "2. Review ~/.claude/settings.local.json and customize as needed"
    echo "3. Review ~/.claude/mcp_servers.json and configure MCP servers"
    echo "4. Run validation: caf agents validate"
    echo ""
    if [ -d "$BACKUP_DIR" ]; then
        echo "Your previous configuration was backed up to:"
        echo "  $BACKUP_DIR"
        echo ""
    fi
else
    echo "============================================"
    echo "Installation completed with $ERRORS error(s)"
    echo "============================================"
    echo "Please check the errors above and fix manually."
    exit 1
fi
