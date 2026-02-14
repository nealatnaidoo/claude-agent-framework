# Sandbox Profiles

Predefined sandbox configurations for different agent operating modes. These profiles control resource limits, network access, and filesystem isolation.

> **Status**: Documentation only. Activation requires testing per-project. See "Activation" section below.

---

## Profiles

### 1. Coding Profile

**Used by**: `back`, `front`
**Purpose**: Standard development work with test execution.

```yaml
profile: coding
sandbox:
  disk: 2048        # 2 GB — room for deps + build artifacts
  network: restricted
  allowedDomains:
    - "pypi.org"
    - "files.pythonhosted.org"
    - "registry.npmjs.org"
    - "github.com"
    - "raw.githubusercontent.com"
  allowedPorts: [5432, 6379, 8000, 8080, 3000, 3001]
  maxProcesses: 50
  timeout: 3600      # 1 hour
```

**Rationale**: Coding agents need to install packages, run builds, and execute tests that may spin up local servers. Network access is limited to package registries and GitHub for dependency resolution.

---

### 2. Research Profile

**Used by**: `design`, `persona`, `lessons`
**Purpose**: Web research and document analysis. No code execution needed.

```yaml
profile: research
sandbox:
  disk: 512          # 512 MB — documents only
  network: open
  allowedDomains: []  # Unrestricted — needs web research
  maxProcesses: 10
  timeout: 1800       # 30 min
```

**Rationale**: Research agents need broad internet access for web searches and fetching reference material. They don't execute code, so process limits are low and disk is minimal.

---

### 3. Batch Profile

**Used by**: `ba`
**Purpose**: Document generation with limited tool access.

```yaml
profile: batch
sandbox:
  disk: 1024         # 1 GB — artifact generation
  network: denied
  allowedDomains: []
  maxProcesses: 20
  timeout: 2400       # 40 min
```

**Rationale**: BA generates specs, tasklists, and rules from existing project context. No network access needed — all inputs are local files. Moderate disk for YAML/markdown generation.

---

### 4. Deploy Profile

**Used by**: `ops`
**Purpose**: CI/CD operations and deployment execution.

```yaml
profile: deploy
sandbox:
  disk: 4096         # 4 GB — Docker images, build contexts
  network: restricted
  allowedDomains:
    - "fly.io"
    - "api.fly.io"
    - "registry.fly.io"
    - "gitlab.com"
    - "github.com"
    - "docker.io"
    - "registry-1.docker.io"
    - "ghcr.io"
    - "pypi.org"
    - "registry.npmjs.org"
  allowedPorts: [443, 8080, 5432]
  maxProcesses: 100
  timeout: 1800       # 30 min
```

**Rationale**: DevOps needs to build Docker images, push to registries, and interact with deployment platforms. Higher disk allocation for image layers. Network restricted to known deployment targets.

---

### 5. Review Profile

**Used by**: `qa`, `review`, `audit`, `visit`
**Purpose**: Read-only code analysis and test execution.

```yaml
profile: review
sandbox:
  disk: 1024         # 1 GB — test execution artifacts
  network: denied
  allowedDomains: []
  maxProcesses: 30
  timeout: 3600       # 1 hour
```

**Rationale**: Review agents analyze existing code and run quality gates. No network access needed — all code is local. Tests may produce temporary artifacts, hence moderate disk.

---

## Profile Matrix

| Profile | Agents | Disk | Network | Timeout |
|---------|--------|------|---------|---------|
| coding | `back`, `front` | 2 GB | Restricted (registries) | 60 min |
| research | `design`, `persona`, `lessons` | 512 MB | Open | 30 min |
| batch | `ba` | 1 GB | Denied | 40 min |
| deploy | `ops` | 4 GB | Restricted (deploy targets) | 30 min |
| review | `qa`, `review`, `audit`, `visit` | 1 GB | Denied | 60 min |

---

## Activation

These profiles are **not yet active**. To activate:

1. **Test each profile** in a sandboxed environment to verify agents can complete their tasks
2. **Add to `settings.local.json`** in the SubagentStart hooks using the `sandbox` field
3. **Monitor for issues**: Some agents may need additional domains or higher limits
4. **Iterate**: Adjust limits based on real-world usage patterns

### Example settings.local.json Integration

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "back|front",
        "sandbox": {
          "disk": 2048,
          "network": "restricted",
          "allowedDomains": ["pypi.org", "registry.npmjs.org", "github.com"]
        }
      }
    ]
  }
}
```

### Known Limitations

- Sandbox support depends on the Claude Code runtime version
- Some quality gate tools (bandit, semgrep) may need additional network access for rule updates
- Docker-in-sandbox is not yet supported — `ops` profile may need adjustment
- WebSearch/WebFetch tools bypass network restrictions at the tool level

---

## Security Considerations

- **Principle of least privilege**: Each profile grants only the access needed for that role
- **Network deny-by-default**: Only `research` and `deploy` profiles have network access
- **No profile has unrestricted filesystem access**: All are scoped to the project directory
- **Review agents are read-only**: `disallowedTools: Write, Edit` in frontmatter + denied network
