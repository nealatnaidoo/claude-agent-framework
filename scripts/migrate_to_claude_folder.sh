#!/bin/bash
# Migrate legacy project artifacts to .claude/ folder structure
# Usage: migrate_to_claude_folder.sh <project_slug>

set -e

PROJECT_SLUG="$1"
if [ -z "$PROJECT_SLUG" ]; then
    echo "Usage: $0 <project_slug>"
    echo "Example: $0 risk_engine"
    exit 1
fi

echo "Migrating $PROJECT_SLUG to .claude/ structure..."

# Create folder structure
echo "Creating folder structure..."
mkdir -p .claude/{artifacts,evolution,remediation,evidence}

# Move artifacts with sequence numbers
echo "Moving artifacts..."
[ -f "${PROJECT_SLUG}_spec.md" ] && mv "${PROJECT_SLUG}_spec.md" .claude/artifacts/002_spec_v1.md && echo "  Moved spec"
[ -f "${PROJECT_SLUG}_tasklist.md" ] && mv "${PROJECT_SLUG}_tasklist.md" .claude/artifacts/003_tasklist_v1.md && echo "  Moved tasklist"
[ -f "${PROJECT_SLUG}_rules.yaml" ] && mv "${PROJECT_SLUG}_rules.yaml" .claude/artifacts/004_rules_v1.yaml && echo "  Moved rules"
[ -f "${PROJECT_SLUG}_quality_gates.md" ] && mv "${PROJECT_SLUG}_quality_gates.md" .claude/artifacts/005_quality_gates_v1.md && echo "  Moved quality_gates"
[ -f "${PROJECT_SLUG}_lessons_applied.md" ] && mv "${PROJECT_SLUG}_lessons_applied.md" .claude/artifacts/006_lessons_applied_v1.md && echo "  Moved lessons_applied"
[ -f "${PROJECT_SLUG}_coding_agent_system_prompt.md" ] && mv "${PROJECT_SLUG}_coding_agent_system_prompt.md" .claude/artifacts/007_coding_prompt_v1.md && echo "  Moved coding_prompt"

# Move evolution logs
echo "Moving evolution logs..."
[ -f "${PROJECT_SLUG}_evolution.md" ] && mv "${PROJECT_SLUG}_evolution.md" .claude/evolution/evolution.md && echo "  Moved evolution"
[ -f "${PROJECT_SLUG}_decisions.md" ] && mv "${PROJECT_SLUG}_decisions.md" .claude/evolution/decisions.md && echo "  Moved decisions"

# Move evidence artifacts
echo "Moving evidence..."
[ -f "artifacts/quality_gates_run.json" ] && mv artifacts/quality_gates_run.json .claude/evidence/ && echo "  Moved quality_gates_run.json"
[ -f "artifacts/test_report.json" ] && mv artifacts/test_report.json .claude/evidence/ && echo "  Moved test_report.json"
[ -f "artifacts/test_failures.json" ] && mv artifacts/test_failures.json .claude/evidence/ && echo "  Moved test_failures.json"
[ -f "artifacts/coverage.json" ] && mv artifacts/coverage.json .claude/evidence/ && echo "  Moved coverage.json"

# Clean up old artifacts folder
rmdir artifacts 2>/dev/null && echo "  Removed empty artifacts folder" || true

# Create initial remediation_tasks.md
if [ ! -f ".claude/remediation/remediation_tasks.md" ]; then
    echo "Creating remediation_tasks.md..."
    cat > .claude/remediation/remediation_tasks.md << 'EOF'
# Remediation Tasks

Last updated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Critical / High Priority

| ID | Type | Summary | Source | Status |
|----|------|---------|--------|--------|
| - | - | No critical items | - | - |

## Medium Priority

| ID | Type | Summary | Source | Status |
|----|------|---------|--------|--------|
| - | - | No medium items | - | - |

## Low Priority

| ID | Type | Summary | Source | Status |
|----|------|---------|--------|--------|
| - | - | No low items | - | - |

## Resolved

| ID | Type | Summary | Resolved | Resolution |
|----|------|---------|----------|------------|
| - | - | No resolved items | - | - |
EOF
fi

# Create manifest template
echo "Creating manifest.yaml template..."
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > .claude/manifest.yaml << EOF
schema_version: "1.0"
project_slug: "${PROJECT_SLUG}"
project_name: "${PROJECT_SLUG}"  # Update with human-readable name
created: "${TIMESTAMP}"
last_updated: "${TIMESTAMP}"
phase: "coding"  # Update as needed: solution_design | ba | coding | qa | code_review | complete
phase_started: "${TIMESTAMP}"

artifact_versions:
EOF

# Add artifact versions based on what was migrated
[ -f ".claude/artifacts/002_spec_v1.md" ] && cat >> .claude/manifest.yaml << EOF
  spec:
    version: 1
    file: ".claude/artifacts/002_spec_v1.md"
    created: "${TIMESTAMP}"
EOF

[ -f ".claude/artifacts/003_tasklist_v1.md" ] && cat >> .claude/manifest.yaml << EOF
  tasklist:
    version: 1
    file: ".claude/artifacts/003_tasklist_v1.md"
    created: "${TIMESTAMP}"
EOF

[ -f ".claude/artifacts/004_rules_v1.yaml" ] && cat >> .claude/manifest.yaml << EOF
  rules:
    version: 1
    file: ".claude/artifacts/004_rules_v1.yaml"
    created: "${TIMESTAMP}"
EOF

[ -f ".claude/artifacts/005_quality_gates_v1.md" ] && cat >> .claude/manifest.yaml << EOF
  quality_gates:
    version: 1
    file: ".claude/artifacts/005_quality_gates_v1.md"
    created: "${TIMESTAMP}"
EOF

[ -f ".claude/artifacts/006_lessons_applied_v1.md" ] && cat >> .claude/manifest.yaml << EOF
  lessons_applied:
    version: 1
    file: ".claude/artifacts/006_lessons_applied_v1.md"
    created: "${TIMESTAMP}"
EOF

[ -f ".claude/artifacts/007_coding_prompt_v1.md" ] && cat >> .claude/manifest.yaml << EOF
  coding_prompt:
    version: 1
    file: ".claude/artifacts/007_coding_prompt_v1.md"
    created: "${TIMESTAMP}"
EOF

# Add outstanding and reviews sections
cat >> .claude/manifest.yaml << EOF

outstanding:
  tasks: []  # TODO: Populate from tasklist - pending/in_progress tasks
  remediation: []

reviews:
  last_qa_review: null
  last_code_review: null
  last_project_review: null

evidence:
EOF

[ -f ".claude/evidence/quality_gates_run.json" ] && echo '  quality_gates_run: ".claude/evidence/quality_gates_run.json"' >> .claude/manifest.yaml
[ -f ".claude/evidence/test_report.json" ] && echo '  test_report: ".claude/evidence/test_report.json"' >> .claude/manifest.yaml
[ -f ".claude/evidence/test_failures.json" ] && echo '  test_failures: ".claude/evidence/test_failures.json"' >> .claude/manifest.yaml

echo ""
echo "Migration complete!"
echo ""
echo "Next steps:"
echo "1. Review .claude/manifest.yaml and update:"
echo "   - project_name (human-readable)"
echo "   - phase (current workflow phase)"
echo "   - outstanding.tasks (parse from tasklist)"
echo "2. Run: tree .claude/"
echo "3. Commit: git add .claude/ && git add -u && git commit -m 'Migrate to .claude/ folder structure'"
