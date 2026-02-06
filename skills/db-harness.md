---
description: Database governance checks - schema drift, FK integrity, PII detection
---

<db-harness>

## Database Harness

Run database governance checks for projects with database dependencies.

### Available Checks

#### 1. Schema Drift Detection
Compare current database schema against expected schema definition.
```bash
# Check for schema drift
python -c "from db_harness import check_schema_drift; check_schema_drift()"
```

#### 2. Foreign Key Integrity
Verify all FK constraints are valid and no orphaned records exist.

#### 3. PII Detection
Scan for personally identifiable information in non-masked columns.
Masking rules: `~/.claude/patterns/db-harness/baseline_masking_rules.yaml`

#### 4. Audit Trail Verification
Ensure audit columns (created_at, updated_at, created_by) exist on all tables.

### CI/CD Integration

GitHub Actions workflows available at:
- `~/.claude/patterns/db-harness/github-actions/schema-drift.yml`
- `~/.claude/patterns/db-harness/github-actions/fk-integrity.yml`
- `~/.claude/patterns/db-harness/github-actions/pii-detection.yml`

GitLab CI template:
- `~/.claude/patterns/db-harness/gitlab-ci-templates.yml`

### DevOps Governor Integration

The DevOps Governor uses db-harness as a deployment gate:
- Schema drift check must pass before deployment
- PII detection must pass before production deployment
- FK integrity runs post-deployment as validation

Full reference: `~/.claude/patterns/db-harness/`

</db-harness>
