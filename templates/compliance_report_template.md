# Framework Compliance Report

**Date**: YYYY-MM-DD
**Version**: {framework_version}
**Verifier**: audit v1.0.0

## Executive Summary

| Category | Pass | Fail | Warnings |
|----------|------|------|----------|
| Prime Directive Alignment | N | N | N |
| Exclusive Permissions | N | N | N |
| Manifest-First Protocol | N | N | N |
| BA-Only Input Constraint | N | N | N |
| ID Sequencing Protocol | N | N | N |
| Document Locations | N | N | N |
| Schema Compliance | N | N | N |
| Slash Command Compliance | N | N | N |
| **TOTAL** | **N** | **N** | **N** |

**Overall Status**: COMPLIANT / NON-COMPLIANT / COMPLIANT_WITH_WARNINGS

---

## Category 1: Prime Directive Alignment

### Checks Performed
| Agent | Prime Directive Reference | Evidence Requirements | Manifest Update |
|-------|--------------------------|----------------------|-----------------|
| back | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| qa | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| ... | ... | ... | ... |

### Failures
{List any failures with specific locations}

### Recommendations
{What needs to be fixed}

---

## Category 2: Exclusive Permissions

### Coding Restriction Verification
| Agent | Has Restriction | Restriction Text |
|-------|-----------------|------------------|
| ba | PASS/FAIL | "{text}" |
| qa | PASS/FAIL | "{text}" |
| ... | ... | ... |

### Deployment Restriction Verification
| Agent | Has Restriction | Restriction Text |
|-------|-----------------|------------------|
| back | PASS/FAIL | "{text}" |
| ... | ... | ... |

### Failures
{List any missing restrictions}

---

## Category 3: Manifest-First Protocol

### Startup Protocol Verification
| Agent | Has Protocol | First Action |
|-------|--------------|--------------|
| back | PASS/FAIL | "Read manifest" |
| ... | ... | ... |

### Hardcoded Path Check
| Agent | Hardcoded Paths Found |
|-------|----------------------|
| {agent} | {list or "None"} |

---

## Category 4: BA-Only Input Constraint

### Coding Agent Verification
| Check | Status |
|-------|--------|
| BA-only constraint documented | PASS/FAIL |
| User rejection message present | PASS/FAIL |
| Redirect to BA workflow documented | PASS/FAIL |

---

## Category 5: ID Sequencing Protocol

### Agents Creating IDs
| Agent | Has Protocol | Search Step | Increment Step |
|-------|--------------|-------------|----------------|
| qa | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| review | PASS/FAIL | PASS/FAIL | PASS/FAIL |

---

## Category 6: Document Locations

### Canonical Location Verification
| Output Type | Correct Location Used | Non-.claude/ References |
|-------------|----------------------|------------------------|
| Artifacts | PASS/FAIL | {list or "None"} |
| Evidence | PASS/FAIL | {list or "None"} |
| Remediation | PASS/FAIL | {list or "None"} |

---

## Category 7: Schema Compliance

### Validation Script Results
```
{Output from python ~/.claude/scripts/validate_agents.py}
```

### Individual Agent Status
| Agent | Frontmatter | Identity | Protocol | Output | Hard Rules |
|-------|-------------|----------|----------|--------|------------|
| {name} | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL | PASS/FAIL |

---

## Category 8: Slash Command Compliance

| Command | allowed-tools | Valid Syntax | Path References |
|---------|---------------|--------------|-----------------|
| /commit | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| /learn | PASS/FAIL | PASS/FAIL | PASS/FAIL |
| ... | ... | ... | ... |

---

## Simulation Exercise Results

### Exercise 1: Coding Exclusivity
- **Status**: PASS/FAIL
- **Observed Behavior**: {description}
- **Evidence**: {file paths, screenshots}

### Exercise 2: BA-Only Input
- **Status**: PASS/FAIL
- **Observed Behavior**: {description}

### Exercise 3: Deployment Exclusivity
- **Status**: PASS/FAIL
- **Observed Behavior**: {description}

### Exercise 4: Manifest-First Protocol
- **Status**: PASS/FAIL
- **Observed Behavior**: {description}

### Exercise 5: ID Sequencing
- **Status**: PASS/FAIL
- **Observed Behavior**: {description}

---

## Remediation Required

### Critical (Must Fix)

| ID | Category | Issue | Agent/File | Fix |
|----|----------|-------|------------|-----|
| COMP-001 | {cat} | {issue} | {file} | {fix} |

### High (Should Fix)

| ID | Category | Issue | Agent/File | Fix |
|----|----------|-------|------------|-----|
| COMP-002 | {cat} | {issue} | {file} | {fix} |

### Medium (Consider)

| ID | Category | Issue | Agent/File | Fix |
|----|----------|-------|------------|-----|
| COMP-003 | {cat} | {issue} | {file} | {fix} |

---

## Verification Commands

To re-run specific checks:

```bash
# Full validation
python ~/.claude/scripts/validate_agents.py

# Category-specific
grep -r "Create/modify source code.*NO" ~/.claude/agents/
grep -r "manifest.*FIRST" ~/.claude/agents/
grep -r "ID Sequencing" ~/.claude/agents/
```

---

## Sign-Off

- [ ] All critical issues resolved
- [ ] All high issues resolved or documented
- [ ] Simulation exercises pass
- [ ] Ready for production use

**Verified By**: audit
**Date**: YYYY-MM-DD
