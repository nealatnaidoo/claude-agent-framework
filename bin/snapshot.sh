#!/bin/bash
# Creates a timestamped snapshot of the current framework state
# Usage: ./snapshot.sh [description]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSIONS_DIR="$REPO_DIR/versions/snapshots"

VERSION=$(cat "$REPO_DIR/VERSION" 2>/dev/null || echo "unknown")
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
DESCRIPTION="${1:-snapshot}"

# Sanitize description for filename
SAFE_DESC=$(echo "$DESCRIPTION" | tr ' ' '-' | tr -cd '[:alnum:]-_')
SNAPSHOT_NAME="${TIMESTAMP}_v${VERSION}_${SAFE_DESC}"

echo "Creating snapshot: $SNAPSHOT_NAME"

mkdir -p "$VERSIONS_DIR"

# Create tarball of all content (excluding .git, versions/snapshots)
cd "$REPO_DIR"
tar --exclude='.git' \
    --exclude='versions/snapshots/*.tar.gz' \
    -czf "$VERSIONS_DIR/${SNAPSHOT_NAME}.tar.gz" \
    agents/ prompts/ schemas/ docs/ lenses/ patterns/ templates/ \
    commands/ hooks/ scripts/ knowledge/ config/ migrations/ \
    CLAUDE.md VERSION manifest.yaml README.md 2>/dev/null || true

# Update versions manifest
cat >> "$REPO_DIR/versions/manifest.yaml" << EOF

  - id: "$SNAPSHOT_NAME"
    version: "$VERSION"
    timestamp: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    description: "$DESCRIPTION"
    file: "snapshots/${SNAPSHOT_NAME}.tar.gz"
EOF

echo ""
echo "Snapshot created: $VERSIONS_DIR/${SNAPSHOT_NAME}.tar.gz"
echo "Manifest updated: $REPO_DIR/versions/manifest.yaml"
