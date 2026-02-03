# db-harness GitHub Actions Templates

Reusable GitHub Actions workflows for implementing database non-negotiables (NN-DB-1 through NN-DB-4).

## Available Workflows

| Workflow | Gate | Purpose |
|----------|------|---------|
| `schema-drift.yml` | NN-DB-1 | Pre-migration schema drift detection |
| `fk-integrity.yml` | NN-DB-2 | Post-migration FK integrity validation |
| `pii-detection.yml` | NN-DB-3 | PII detection and masking rule coverage |
| `propagate.yml` | NN-DB-3 | Full database propagation with PII masking |

## Quick Start

### 1. Copy Templates to Your Repository

```bash
# From your project root
mkdir -p .github/workflows
cp ~/.claude/devops/patterns/db-harness/github-actions/*.yml .github/workflows/
```

### 2. Configure Secrets

Add these secrets to your GitHub repository:

| Secret | Required | Description |
|--------|----------|-------------|
| `DB_PROD_CONN` | For remote DBs | Production database connection string |
| `DB_DEV_CONN` | For remote DBs | Dev database connection string |
| `FLY_API_TOKEN` | For Fly.io | Fly.io API token for proxy access |

### 3. Use in Your Workflow

```yaml
# .github/workflows/database-gates.yml
name: Database Gates

on:
  push:
    branches: [main]
    paths:
      - 'migrations/**'
  pull_request:
    branches: [main]
    paths:
      - 'migrations/**'

jobs:
  # NN-DB-1: Schema Drift Check
  schema-drift:
    uses: ./.github/workflows/schema-drift.yml
    with:
      source_db: "sqlite:///dev.db"
      target_db: "sqlite:///staging.db"
      fail_on_breaking: true

  # NN-DB-2: FK Integrity (after drift passes)
  fk-integrity:
    needs: schema-drift
    uses: ./.github/workflows/fk-integrity.yml
    with:
      database: "sqlite:///app.db"
      tolerance: "0.0"

  # NN-DB-3: PII Detection
  pii-detection:
    uses: ./.github/workflows/pii-detection.yml
    with:
      database: "sqlite:///app.db"
      masking_rules: ".claude/db-harness/masking_rules.yaml"
      tables: "users,sessions"
```

## Fly.io Integration

For databases hosted on Fly.io, use the proxy configuration:

```yaml
jobs:
  propagate:
    uses: ./.github/workflows/propagate.yml
    with:
      use_fly_proxy: true
      fly_app_name: "your-app-name"
      fly_proxy_port: "5432"
    secrets:
      fly_api_token: ${{ secrets.FLY_API_TOKEN }}
      source_conn: "postgresql://user:pass@localhost:5432/db"
      target_conn: "sqlite:///dev.db"
```

## Exit Codes

All workflows use semantic exit codes:

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue pipeline |
| 1 | General error | Check logs |
| 2 | Breaking drift detected (NN-DB-1) | Fix schema differences |
| 3 | FK violations detected (NN-DB-2) | Fix FK constraints |

## Evidence Artifacts

All workflows upload evidence artifacts retained for 365 days:

- `drift-evidence-{run_id}` - Schema drift reports
- `consistency-evidence-{run_id}` - FK integrity reports
- `pii-evidence-{run_id}` - PII detection results
- `propagation-evidence-{run_id}` - Propagation results

## Decision References

- DEC-DEVOPS-009: Fly.io database access via proxy
- DEC-DEVOPS-010: Baseline masking rules location
- DEC-DEVOPS-011: Audit log retention (1 year)
- DEC-DEVOPS-014: db-harness integration
