# DevOps Portfolio Structure

## Overview

This document defines the canonical structure for DevOps Governor cross-project visibility.

**Decision Reference**: DEC-DEVOPS-020

## Repository Strategy: Polyrepo with Shared Templates

```
Portfolio Structure
├── gitlab.com/your-org/
│   │
│   ├── devops-templates/             # SHARED CI/CD TEMPLATES
│   │   ├── .gitlab/
│   │   │   └── ci-templates/
│   │   │       ├── python-fly.yml
│   │   │       ├── python-aks.yml
│   │   │       ├── python-functions.yml
│   │   │       ├── nextjs-frontend.yml
│   │   │       ├── databricks-jobs.yml
│   │   │       ├── quality-gates.yml
│   │   │       └── security-scanning.yml
│   │   └── README.md
│   │
│   ├── infrastructure/               # TERRAFORM/PULUMI
│   │   ├── modules/
│   │   │   ├── aks-cluster/
│   │   │   ├── function-app/
│   │   │   ├── fly-app/
│   │   │   └── databricks-workspace/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── prod/
│   │   └── .gitlab-ci.yml
│   │
│   └── apps/                         # APPLICATION REPOS
│       ├── app-web/
│       ├── app-api/
│       ├── analytics-pipeline/
│       └── event-processor/
```

## Automation Levels by Environment

| Environment | Trigger | Approval | Rollback |
|-------------|---------|----------|----------|
| **dev** | Auto on merge to `develop` | None | Auto via pipeline |
| **staging** | Auto on merge to `main` | None (gates must pass) | Manual |
| **production** | Manual button | Required (1 approver) | Manual or auto on health fail |

## Automation Levels by Workload Type

| Workload | Dev | Staging | Prod | Notes |
|----------|-----|---------|------|-------|
| **Fly.io Apps** | Auto | Auto | Manual | Edge apps, fast rollback |
| **Azure AKS** | Auto | Auto + gate | Manual | Blue-green in prod |
| **Azure Functions** | Auto | Auto | Manual + slot swap | Zero-downtime via slots |
| **Databricks** | Auto | Auto | Manual | Separate lifecycle |

## Project Template

Every project MUST have this structure for DevOps Governor visibility:

```
{project}/
├── .gitlab-ci.yml                    # Includes shared templates
├── .claude/
│   ├── manifest.yaml                 # Project state
│   └── evidence/                     # Quality gate outputs
├── k8s/                              # If using AKS
│   ├── base/
│   └── overlays/{dev,staging,prod}/
├── fly.toml                          # If using Fly.io
├── fly.dev.toml
├── Dockerfile
└── README.md
```

## Shared Template Inclusion

Projects inherit from shared templates:

```yaml
# .gitlab-ci.yml in each project

include:
  - project: 'your-org/devops-templates'
    ref: main
    file: '.gitlab/ci-templates/quality-gates.yml'
  - project: 'your-org/devops-templates'
    ref: main
    file: '.gitlab/ci-templates/python-aks.yml'

# Override variables as needed
variables:
  AKS_CLUSTER_DEV: "my-project-dev"
  ACR_REGISTRY_NAME: "myregistry"
```

## DevOps Governor Registry

The DevOps Governor maintains a central registry:

```yaml
# ~/.claude/devops/project_registry.yaml

projects:
  - slug: "app-web"
    repo: "gitlab.com/your-org/apps/app-web"
    deployment_targets:
      - type: fly
        environments: [dev, prod]
    ci_template: "python-fly.yml"
    last_audit: "2026-02-01"
    compliance_status: compliant

  - slug: "app-api"
    repo: "gitlab.com/your-org/apps/app-api"
    deployment_targets:
      - type: aks
        environments: [dev, staging, prod]
    ci_template: "python-aks.yml"
    last_audit: "2026-02-01"
    compliance_status: compliant

  - slug: "event-processor"
    repo: "gitlab.com/your-org/apps/event-processor"
    deployment_targets:
      - type: azure-functions
        environments: [dev, staging, prod]
    ci_template: "azure-functions-python.yml"
    last_audit: "2026-02-01"
    compliance_status: compliant

  - slug: "analytics-pipeline"
    repo: "gitlab.com/your-org/apps/analytics-pipeline"
    deployment_targets:
      - type: databricks
        environments: [dev, staging, prod]
    ci_template: "databricks-jobs.yml"
    last_audit: "2026-02-01"
    compliance_status: compliant
```

## Cross-Project Metrics Dashboard

The DevOps Governor tracks these metrics across all projects:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Pipeline Success Rate | > 95% | Per project, rolling 7 days |
| Test Coverage | > 80% | Per project |
| Security Scan Pass Rate | 100% | No critical/high vulns |
| Deployment Frequency | Weekly minimum | Per environment |
| Change Failure Rate | < 5% | Rollbacks / deploys |
| MTTR | < 1 hour | Mean time to recovery |

## Branching Strategy

**Trunk-Based Development** with short-lived feature branches:

```
main (production-ready)
├── develop (integration)
└── feature/* (short-lived, max 2 days)
```

**Flow:**
1. Create `feature/XXX` from `develop`
2. Open MR → triggers quality gates
3. Merge to `develop` → auto-deploy to dev
4. Merge `develop` to `main` → auto-deploy to staging
5. Manual promotion → deploy to production

## Deployment Strategies by Workload

### Fly.io (Edge Apps)
- **Strategy**: Rolling deployment with health checks
- **Rollback**: `flyctl releases rollback`
- **Zero-downtime**: Built-in

### Azure AKS (Kubernetes)
- **Strategy**: Blue-green deployment
- **Rollback**: Switch service selector back
- **Zero-downtime**: Via service selector swap

### Azure Functions (Serverless)
- **Strategy**: Slot deployment + swap
- **Rollback**: Swap back to previous slot
- **Zero-downtime**: Via slot swap

### Databricks (Analytics)
- **Strategy**: Versioned wheel + job update
- **Rollback**: Point job to previous wheel version
- **Note**: Separate lifecycle from app deployments

## Non-Negotiables (ALL Workloads)

Every deployment target MUST have:

1. **Quality Gates**: lint, type-check, unit tests, security tests
2. **Security Scanning**: SAST, secret detection, dependency scanning
3. **Environment Separation**: dev/staging/prod
4. **Health Checks**: Post-deployment validation
5. **Rollback Plan**: Documented and tested
6. **Metrics**: Coverage and pipeline success rate

## Audit Schedule

| Audit Type | Frequency | Performed By |
|------------|-----------|--------------|
| Template Drift | Weekly | DevOps Governor (automated) |
| Security Compliance | Monthly | DevOps Governor + Security Review |
| Full Portfolio Audit | Quarterly | DevOps Governor (manual) |
