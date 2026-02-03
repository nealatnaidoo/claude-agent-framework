# db-harness Integration Guide

DevOps Governor portfolio-wide database propagation, migration gates, and compliance tooling.

---

## Overview

db-harness provides:

| Capability | Description | Gate Type |
|------------|-------------|-----------|
| Schema Drift Detection | Catch breaking changes before deployment | Blocking |
| FK Integrity Validation | Verify referential integrity after migrations | Blocking |
| PII Masking | Protect sensitive data in lower environments | Blocking |
| Audit Trail | Tamper-evident logging for compliance | Warning |

---

## Non-Negotiables (NN-DB-*)

These gates are **required** for all projects with databases:

### NN-DB-1: Pre-Migration Schema Drift Check

**When**: Before deploying migrations to staging/production
**Threshold**: 0 breaking schema changes
**Type**: BLOCKING

```yaml
# .gitlab-ci.yml
schema-drift-check:
  extends: .db-harness-drift-check
  variables:
    SOURCE_CONN: "${DB_DEV_CONN}"
    TARGET_CONN: "${DB_STAGING_CONN}"
```

### NN-DB-2: Post-Migration FK Integrity

**When**: After running migrations in any environment
**Threshold**: 0 foreign key violations
**Type**: BLOCKING

```yaml
verify-migration:
  extends: .db-harness-fk-integrity
  variables:
    SOURCE_CONN: "${DB_BACKUP_CONN}"
    TARGET_CONN: "${DB_MIGRATED_CONN}"
    TOLERANCE: "0.05"  # Allow 5% row count difference
```

### NN-DB-3: PII Masking for Environment Propagation

**When**: Refreshing dev/staging from production
**Threshold**: 0 PII detected after masking
**Type**: BLOCKING

```yaml
refresh-prod-to-dev:
  extends: .db-harness-propagate
  variables:
    SOURCE_CONN: "${DB_PROD_CONN}"
    TARGET_CONN: "${DB_DEV_CONN}"
    MASKING_RULES: ".claude/db-harness/masking_rules.yaml"
```

### NN-DB-4: Audit Log Hash Chain

**When**: Periodic compliance check
**Threshold**: Valid hash chain (no tampering)
**Type**: WARNING (non-blocking)

```yaml
audit-verify:
  extends: .db-harness-audit-verify
  variables:
    AUDIT_PATH: ".claude/evidence/db_propagation"
```

---

## Project Setup

### 1. Add CI Template Reference

```yaml
# .gitlab-ci.yml
include:
  - local: '.gitlab/db-harness.yml'
  # Or from central repository:
  # - project: 'devops/ci-templates'
  #   file: '/db-harness/gitlab-ci-templates.yml'
```

### 2. Create Project Masking Rules

```yaml
# .claude/db-harness/masking_rules.yaml
version: "1.0"
baseline_version: "2026-Q1"
extends: "~/.claude/devops/patterns/db-harness/baseline_masking_rules.yaml"

project_overrides:
  # Add project-specific fields
  - table: "users"
    column: "custom_field"
    masking_strategy: "faker"
    faker_provider: "text"
```

### 3. Create Subsetting Rules (Optional)

```yaml
# .claude/db-harness/subsetting_rules.yaml
version: "1.0"
strategy: "hybrid"

percentage:
  sample_percentage: 0.20  # 20%

date_range:
  column: "created_at"
  days: 90

critical_tables:
  - "permissions"
  - "roles"
```

### 4. Configure CI Variables

In GitLab > Settings > CI/CD > Variables:

| Variable | Description | Masked | Protected |
|----------|-------------|--------|-----------|
| `DB_PROD_CONN` | Production connection string | Yes | Yes |
| `DB_STAGING_CONN` | Staging connection string | Yes | No |
| `DB_DEV_CONN` | Dev connection string | Yes | No |

---

## Integration Patterns

### Pattern 1: Merge Request Validation

```yaml
stages:
  - validate
  - test
  - deploy

# Check schema drift on every MR
mr-schema-check:
  extends: .db-harness-drift-check
  stage: validate
  variables:
    SOURCE_CONN: "${DB_DEV_CONN}"
    TARGET_CONN: "${DB_STAGING_CONN}"
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

### Pattern 2: Pre-Production Gate

```yaml
# Manual gate before production deploy
pre-prod-validation:
  extends: .db-harness-pre-deploy
  stage: validate
  variables:
    SOURCE_CONN: "${DB_STAGING_CONN}"
    TARGET_CONN: "${DB_PROD_CONN}"
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: manual
```

### Pattern 3: Scheduled Environment Refresh

```yaml
# Weekly prod-to-dev refresh
weekly-refresh:
  extends: .db-harness-weekly-refresh
  variables:
    SOURCE_CONN: "${DB_PROD_CONN}"
    TARGET_CONN: "${DB_DEV_CONN}"
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
      when: always
```

### Pattern 4: Post-Migration Verification

```yaml
# After running migrations
verify-migrations:
  extends: .db-harness-post-migrate
  stage: verify
  variables:
    PRE_MIGRATION_CONN: "${DB_BACKUP_CONN}"
    TARGET_CONN: "${DB_STAGING_CONN}"
  needs: [run-migrations]
```

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Database Deployment Workflow                          │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │ Merge Request│
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐     ┌─────────────────────────────────────────────────┐
  │ NN-DB-1:     │────▶│ Schema Drift Check                              │
  │ drift check  │     │ db-harness drift dev staging --fail-on-breaking │
  └──────┬───────┘     └─────────────────────────────────────────────────┘
         │
         │ Pass
         ▼
  ┌──────────────┐
  │ Merge to Main│
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐     ┌─────────────────────────────────────────────────┐
  │ Deploy to    │────▶│ Run Migrations                                  │
  │ Staging      │     │ alembic upgrade head                            │
  └──────┬───────┘     └─────────────────────────────────────────────────┘
         │
         ▼
  ┌──────────────┐     ┌─────────────────────────────────────────────────┐
  │ NN-DB-2:     │────▶│ FK Integrity Check                              │
  │ consistency  │     │ db-harness consistency backup staging           │
  └──────┬───────┘     └─────────────────────────────────────────────────┘
         │
         │ Pass
         ▼
  ┌──────────────┐
  │ Deploy to    │
  │ Production   │
  └──────────────┘


  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    Weekly Environment Refresh                            │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │ Schedule     │ (Monday 2 AM)
  │ Trigger      │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐     ┌─────────────────────────────────────────────────┐
  │ NN-DB-3:     │────▶│ Propagate Prod → Dev                            │
  │ propagate    │     │ db-harness propagate prod dev --mask-pii        │
  └──────┬───────┘     └─────────────────────────────────────────────────┘
         │
         ▼
  ┌──────────────┐     ┌─────────────────────────────────────────────────┐
  │ NN-DB-3b:    │────▶│ Post-Mask PII Verification                      │
  │ detect-pii   │     │ db-harness detect-pii dev --sample-size 1000    │
  └──────┬───────┘     └─────────────────────────────────────────────────┘
         │
         │ 0 PII matches
         ▼
  ┌──────────────┐
  │ Dev Ready    │
  │ for Testing  │
  └──────────────┘
```

---

## Compliance Notes

### GDPR/CCPA Requirements

- All EU user data MUST use `baseline_masking_rules.yaml`
- IP addresses MUST be nulled (not just masked)
- Audit logs retained for minimum 1 year

### HIPAA Requirements

- Health data requires additional masking rules
- Consult DevOps Governor for healthcare projects

### SOC 2 Requirements

- Audit trail hash chain must be verified monthly
- Evidence artifacts retained in `.claude/evidence/`

---

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue pipeline |
| 1 | General error | Check logs |
| 2 | Breaking schema drift | Block deployment |
| 3 | FK violations | Block deployment |

---

## Troubleshooting

### "Breaking schema drift detected"

1. Review drift report in `.claude/evidence/drift_*.json`
2. Apply missing migrations to target environment
3. Or: downgrade migration to be backward-compatible

### "FK violations detected"

1. Review consistency report
2. Check subsetting rules `cascade_selection: true`
3. Increase `max_cascade_depth` if needed

### "PII still detected after masking"

1. Review post-mask PII report
2. Add missing fields to masking rules
3. Re-run propagation

---

## See Also

- [db-harness Documentation](/Users/naidooone/Developer/db-harness/docs/)
- [Baseline Masking Rules](./baseline_masking_rules.yaml)
- [GitLab CI Templates](./gitlab-ci-templates.yml)
- [DevOps Governor Manifest](~/.claude/devops/manifest.yaml)
