#!/bin/bash
# Test the framework install in a clean Docker container
#
# Usage:
#   ./test-install/run.sh              # Build and drop into shell
#   ./test-install/run.sh --validate   # Build and run validation checks
#   ./test-install/run.sh --branch feature-x  # Test a specific branch

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BRANCH="main"
MODE="shell"

while [[ $# -gt 0 ]]; do
    case $1 in
        --validate) MODE="validate"; shift ;;
        --branch) BRANCH="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

IMAGE_NAME="caf-test-install"

echo "============================================"
echo "Testing fresh install (branch: $BRANCH)"
echo "============================================"
echo ""

docker build \
    --build-arg BRANCH="$BRANCH" \
    -t "$IMAGE_NAME" \
    -f "$SCRIPT_DIR/Dockerfile" \
    "$REPO_DIR"

if [ "$MODE" = "validate" ]; then
    echo ""
    echo "Running validation..."
    docker run --rm "$IMAGE_NAME" bash -c '
        echo "=== Symlinks ==="
        ls -la ~/.claude/agents ~/.claude/CLAUDE.md ~/.claude/hooks 2>&1 | head -5

        echo ""
        echo "=== caf CLI ==="
        caf --help | head -5

        echo ""
        echo "=== Agent validation ==="
        caf agents validate 2>&1

        echo ""
        echo "=== Tests ==="
        cd ~/claude-agent-framework && python -m pytest tests/ -q --tb=line 2>&1 | tail -5

        echo ""
        echo "=== Settings files ==="
        echo "settings.json:"
        cat ~/.claude/settings.json
        echo ""
        echo "settings.local.json (hooks count):"
        python3 -c "import json; d=json.load(open(\"$HOME/.claude/settings.local.json\")); print(f\"  defaultMode: {d[\"permissions\"][\"defaultMode\"]}\"); print(f\"  hook events: {len(d[\"hooks\"])}\")"

        echo ""
        echo "=== No personal paths ==="
        if grep -r "/Users/naidooone" ~/.claude/agents/ ~/.claude/skills/ ~/.claude/CLAUDE.md 2>/dev/null; then
            echo "FAIL: Personal paths found!"
            exit 1
        else
            echo "PASS: No personal paths in agents/skills/CLAUDE.md"
        fi

        echo ""
        echo "=== Welcome text exists ==="
        if [ -f ~/claude-agent-framework/bin/welcome.txt ]; then
            echo "PASS"
        else
            echo "FAIL"
            exit 1
        fi

        echo ""
        echo "============================================"
        echo "ALL CHECKS PASSED"
        echo "============================================"
    '
else
    echo ""
    echo "Dropping into container shell..."
    echo "  Try: caf --help, caf agents validate, ls -la ~/.claude/"
    echo ""
    docker run --rm -it "$IMAGE_NAME"
fi
