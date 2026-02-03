#!/bin/bash
# Rollback to a previous snapshot
# Usage: ./rollback.sh <snapshot-name>
# List available: ./rollback.sh --list

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSIONS_DIR="$REPO_DIR/versions/snapshots"

if [ "$1" == "--list" ] || [ -z "$1" ]; then
    echo "Available snapshots:"
    echo ""
    if [ -d "$VERSIONS_DIR" ]; then
        ls -1 "$VERSIONS_DIR"/*.tar.gz 2>/dev/null | while read f; do
            basename "$f" .tar.gz
        done
    else
        echo "  (no snapshots found)"
    fi
    echo ""
    echo "Usage: ./rollback.sh <snapshot-name>"
    exit 0
fi

SNAPSHOT_NAME="$1"
SNAPSHOT_FILE="$VERSIONS_DIR/${SNAPSHOT_NAME}.tar.gz"

if [ ! -f "$SNAPSHOT_FILE" ]; then
    # Try with .tar.gz extension
    SNAPSHOT_FILE="$VERSIONS_DIR/${SNAPSHOT_NAME}"
    if [ ! -f "$SNAPSHOT_FILE" ]; then
        echo "ERROR: Snapshot not found: $SNAPSHOT_NAME"
        echo "Run './rollback.sh --list' to see available snapshots."
        exit 1
    fi
fi

echo "============================================"
echo "Rollback to: $SNAPSHOT_NAME"
echo "============================================"
echo ""
echo "WARNING: This will overwrite current content with the snapshot."
echo "Current state will be backed up first."
echo ""

read -p "Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Rollback cancelled."
    exit 0
fi

# Create backup of current state first
BACKUP_NAME="pre-rollback-$(date +%Y%m%d-%H%M%S)"
echo ""
echo "Creating backup: $BACKUP_NAME"
"$SCRIPT_DIR/snapshot.sh" "$BACKUP_NAME"

# Extract snapshot (overwrite)
echo ""
echo "Extracting snapshot..."
cd "$REPO_DIR"
tar -xzf "$SNAPSHOT_FILE"

echo ""
echo "============================================"
echo "Rollback complete"
echo "============================================"
echo ""
echo "Rolled back to: $SNAPSHOT_NAME"
echo "Previous state backed up as: $BACKUP_NAME"
echo ""
echo "Note: ~/.claude/ symlinks should still work, but you may want to"
echo "re-run the installer if you encounter issues."
