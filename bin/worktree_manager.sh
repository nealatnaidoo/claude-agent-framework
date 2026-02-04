#!/usr/bin/env bash
#
# Worktree Manager - Helper script for BA agent worktree operations
# Usage: worktree_manager.sh <command> [args]
#
# Part of Claude Code v1.2 worktree integration
# Created: 2026-01-31
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================================
# Commands
# ============================================================

cmd_create() {
    local project_slug="$1"
    local feature_slug="$2"

    if [[ -z "$project_slug" || -z "$feature_slug" ]]; then
        log_error "Usage: worktree_manager.sh create <project_slug> <feature_slug>"
        exit 1
    fi

    local worktree_path="../${project_slug}-${feature_slug}"
    local branch_name="feature/${feature_slug}"

    log_info "Creating worktree for feature: $feature_slug"

    # Check if worktree already exists
    if git worktree list | grep -q "$worktree_path"; then
        log_error "Worktree already exists at $worktree_path"
        exit 1
    fi

    # Create feature branch from main/master
    log_info "Creating branch: $branch_name"
    local base_branch="main"
    git rev-parse --verify main >/dev/null 2>&1 || base_branch="master"
    git branch "$branch_name" "$base_branch"

    # Create worktree (from current branch, checking out the new branch)
    log_info "Creating worktree at: $worktree_path"
    git worktree add "$worktree_path" "$branch_name"

    # Initialize .claude structure
    log_info "Initializing .claude structure"
    mkdir -p "$worktree_path/.claude"/{artifacts,evolution,remediation,evidence}

    # Copy shared artifacts
    if [[ -d ".claude/artifacts" ]]; then
        cp .claude/artifacts/004_rules_v*.yaml "$worktree_path/.claude/artifacts/" 2>/dev/null || true
        cp .claude/artifacts/005_quality_gates_v*.md "$worktree_path/.claude/artifacts/" 2>/dev/null || true
        cp .claude/artifacts/006_lessons_applied_v*.md "$worktree_path/.claude/artifacts/" 2>/dev/null || true
    fi

    # Initialize evolution logs
    touch "$worktree_path/.claude/evolution/evolution.md"
    touch "$worktree_path/.claude/evolution/decisions.md"

    log_success "Worktree created at: $worktree_path"
    log_info "Next steps:"
    echo "  1. Create feature spec: $worktree_path/.claude/artifacts/002_spec_${feature_slug}_v1.md"
    echo "  2. Create feature tasklist: $worktree_path/.claude/artifacts/003_tasklist_${feature_slug}_v1.md"
    echo "  3. Create worktree manifest: $worktree_path/.claude/manifest.yaml"
    echo "  4. Update main manifest with active_worktrees entry"
}

cmd_list() {
    log_info "Active worktrees:"
    git worktree list

    echo ""
    log_info "Worktree phases (from manifests):"

    for worktree in $(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2); do
        if [[ -f "$worktree/.claude/manifest.yaml" ]]; then
            local phase=$(grep "^phase:" "$worktree/.claude/manifest.yaml" | head -1 | awk '{print $2}' | tr -d '"')
            local is_worktree=$(grep "is_worktree:" "$worktree/.claude/manifest.yaml" | head -1 | awk '{print $2}')
            if [[ "$is_worktree" == "true" ]]; then
                echo "  $worktree: $phase (feature worktree)"
            else
                echo "  $worktree: $phase (main)"
            fi
        else
            echo "  $worktree: (no manifest)"
        fi
    done
}

cmd_status() {
    local worktree_path="${1:-.}"

    if [[ ! -f "$worktree_path/.claude/manifest.yaml" ]]; then
        log_error "No manifest found at $worktree_path/.claude/manifest.yaml"
        exit 1
    fi

    log_info "Worktree Status: $worktree_path"
    echo ""

    # Extract key info from manifest
    grep -E "^(phase|project_slug|schema_version):" "$worktree_path/.claude/manifest.yaml" || true

    echo ""
    log_info "Worktree metadata:"
    grep -A10 "^worktree:" "$worktree_path/.claude/manifest.yaml" 2>/dev/null || echo "  (not a feature worktree)"

    echo ""
    log_info "Outstanding tasks:"
    grep -A20 "^outstanding:" "$worktree_path/.claude/manifest.yaml" | head -25 || echo "  (none)"
}

cmd_remove() {
    local worktree_path="$1"

    if [[ -z "$worktree_path" ]]; then
        log_error "Usage: worktree_manager.sh remove <worktree_path>"
        exit 1
    fi

    # Check if worktree exists
    if ! git worktree list | grep -q "$worktree_path"; then
        log_error "Worktree not found: $worktree_path"
        exit 1
    fi

    log_warn "This will remove worktree: $worktree_path"
    read -p "Continue? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Get branch name before removal
        local branch=$(git worktree list --porcelain | grep -A2 "worktree.*$worktree_path" | grep "branch" | sed 's/branch refs\/heads\///')

        # Remove worktree
        git worktree remove "$worktree_path"
        log_success "Worktree removed: $worktree_path"

        # Offer to delete branch
        if [[ -n "$branch" ]]; then
            read -p "Delete branch '$branch'? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git branch -d "$branch" 2>/dev/null || git branch -D "$branch"
                log_success "Branch deleted: $branch"
            fi
        fi
    else
        log_info "Cancelled"
    fi
}

cmd_sync() {
    local worktree_path="$1"

    if [[ -z "$worktree_path" ]]; then
        log_error "Usage: worktree_manager.sh sync <worktree_path>"
        exit 1
    fi

    log_info "Syncing shared artifacts to: $worktree_path"

    # Sync rules
    if ls .claude/artifacts/004_rules_v*.yaml 1>/dev/null 2>&1; then
        cp .claude/artifacts/004_rules_v*.yaml "$worktree_path/.claude/artifacts/"
        log_success "Synced rules"
    fi

    # Sync quality gates
    if ls .claude/artifacts/005_quality_gates_v*.md 1>/dev/null 2>&1; then
        cp .claude/artifacts/005_quality_gates_v*.md "$worktree_path/.claude/artifacts/"
        log_success "Synced quality gates"
    fi

    # Sync lessons
    if ls .claude/artifacts/006_lessons_applied_v*.md 1>/dev/null 2>&1; then
        cp .claude/artifacts/006_lessons_applied_v*.md "$worktree_path/.claude/artifacts/"
        log_success "Synced lessons"
    fi

    log_success "Sync complete"
}

cmd_backlog() {
    local subcmd="${1:-list}"

    case "$subcmd" in
        list)
            log_info "Feature Backlog:"
            if [[ -f ".claude/manifest.yaml" ]]; then
                echo ""
                # Parse backlog using Python/YAML
                python3 << 'PYEOF'
import yaml
import sys

try:
    with open('.claude/manifest.yaml', 'r') as f:
        manifest = yaml.safe_load(f)

    backlog = manifest.get('feature_backlog', [])
    active = manifest.get('active_worktrees', [])
    governance = manifest.get('worktree_governance', {})

    max_parallel = governance.get('max_parallel', 3)
    current = len([w for w in active if w.get('phase') not in ['complete', 'merged']])

    print(f"Capacity: {current}/{max_parallel} worktrees active")
    print(f"Backlog:  {len([f for f in backlog if f.get('status') == 'ready'])} features ready")
    print("")

    if not backlog:
        print("  (empty)")
    else:
        print(f"{'Pri':<4} {'Slug':<20} {'Status':<12} {'Dependencies':<20} {'Worktree':<15}")
        print("-" * 75)
        for feature in sorted(backlog, key=lambda x: x.get('priority', 99)):
            deps = ', '.join(feature.get('dependencies', [])) or '-'
            wt = feature.get('worktree') or '-'
            print(f"{feature.get('priority', '?'):<4} {feature['slug']:<20} {feature['status']:<12} {deps:<20} {wt:<15}")

except Exception as e:
    print(f"Error reading manifest: {e}")
    sys.exit(1)
PYEOF
            else
                log_error "No manifest found"
            fi
            ;;

        next)
            log_info "Finding next feature to spawn..."
            python3 << 'PYEOF'
import yaml

with open('.claude/manifest.yaml', 'r') as f:
    manifest = yaml.safe_load(f)

backlog = manifest.get('feature_backlog', [])
active = manifest.get('active_worktrees', [])
governance = manifest.get('worktree_governance', {})

max_parallel = governance.get('max_parallel', 3)
current = len([w for w in active if w.get('phase') not in ['complete', 'merged']])

if current >= max_parallel:
    print(f"At capacity ({current}/{max_parallel}). Cannot spawn more worktrees.")
    exit(1)

# Find completed features
completed = {f['slug'] for f in backlog if f.get('status') == 'complete'}

# Find ready features with satisfied dependencies
ready = []
for feature in backlog:
    if feature.get('status') != 'ready':
        continue
    deps = set(feature.get('dependencies', []))
    if deps.issubset(completed):
        ready.append(feature)

if not ready:
    print("No features ready to spawn (check dependencies)")
    exit(1)

# Get highest priority
next_feature = min(ready, key=lambda x: x.get('priority', 99))
print(f"Next feature: {next_feature['slug']} (priority {next_feature.get('priority')})")
print(f"Run: worktree_manager.sh spawn-from-backlog {next_feature['slug']}")
PYEOF
            ;;

        *)
            echo "Usage: worktree_manager.sh backlog [list|next]"
            ;;
    esac
}

cmd_spawn_from_backlog() {
    local feature_slug="$1"

    if [[ -z "$feature_slug" ]]; then
        log_error "Usage: worktree_manager.sh spawn-from-backlog <feature_slug>"
        exit 1
    fi

    log_info "Spawning worktree from backlog: $feature_slug"

    # Get project slug from manifest
    local project_slug=$(grep "^project_slug:" .claude/manifest.yaml | awk '{print $2}' | tr -d '"')

    if [[ -z "$project_slug" ]]; then
        log_error "Could not determine project_slug from manifest"
        exit 1
    fi

    # Create the worktree
    cmd_create "$project_slug" "$feature_slug"

    # Copy feature-specific artifacts
    local worktree_path="../${project_slug}-${feature_slug}"

    if [[ -f ".claude/artifacts/002_spec_${feature_slug}_v1.md" ]]; then
        cp ".claude/artifacts/002_spec_${feature_slug}_v1.md" "$worktree_path/.claude/artifacts/"
        log_success "Copied feature spec"
    fi

    if [[ -f ".claude/artifacts/003_tasklist_${feature_slug}_v1.md" ]]; then
        cp ".claude/artifacts/003_tasklist_${feature_slug}_v1.md" "$worktree_path/.claude/artifacts/"
        log_success "Copied feature tasklist"
    fi

    log_info "Next steps:"
    echo "  1. Create worktree manifest: $worktree_path/.claude/manifest.yaml"
    echo "  2. Update main manifest:"
    echo "     - Set feature_backlog[slug=$feature_slug].status = 'in_progress'"
    echo "     - Set feature_backlog[slug=$feature_slug].worktree = '$feature_slug'"
    echo "     - Add entry to active_worktrees"
}

cmd_help() {
    echo "Worktree Manager - Helper for BA agent worktree operations"
    echo ""
    echo "Usage: worktree_manager.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  create <project_slug> <feature_slug>  Create new feature worktree"
    echo "  list                                   List all worktrees with phases"
    echo "  status [worktree_path]                 Show worktree status"
    echo "  remove <worktree_path>                 Remove a worktree"
    echo "  sync <worktree_path>                   Sync shared artifacts to worktree"
    echo ""
    echo "Backlog commands:"
    echo "  backlog list                           Show feature backlog"
    echo "  backlog next                           Find next feature to spawn"
    echo "  spawn-from-backlog <feature_slug>      Spawn worktree for backlog feature"
    echo ""
    echo "  help                                   Show this help"
}

# ============================================================
# Main
# ============================================================

case "${1:-help}" in
    create)             cmd_create "${2:-}" "${3:-}" ;;
    list)               cmd_list ;;
    status)             cmd_status "${2:-}" ;;
    remove)             cmd_remove "${2:-}" ;;
    sync)               cmd_sync "${2:-}" ;;
    backlog)            cmd_backlog "${2:-}" ;;
    spawn-from-backlog) cmd_spawn_from_backlog "${2:-}" ;;
    help)               cmd_help ;;
    *)                  log_error "Unknown command: $1"; cmd_help; exit 1 ;;
esac
