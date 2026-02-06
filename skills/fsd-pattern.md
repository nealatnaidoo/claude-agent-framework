---
description: Apply Feature-Sliced Design pattern to a React/TypeScript frontend
---

<fsd-pattern>

## Feature-Sliced Design Pattern

Apply this pattern when creating or validating React/TypeScript frontend code.

### Layer Hierarchy (strict, downward imports ONLY)

```
src/
  app/         # Providers, routing, global styles (composition only)
  pages/       # Route components (THIN - compose widgets/features, NO logic)
  widgets/     # Composite UI blocks (combine features + entities)
  features/    # User interactions (forms, buttons, modals)
  entities/    # Domain objects (user card, product item)
  shared/      # UI kit, utilities, types, API clients
```

### Import Rules (INVIOLABLE)

- **NO upward imports** (lower layer MUST NOT import from higher) = BUILD FAIL
- **NO same-layer cross-slice imports** (features/auth MUST NOT import features/payment)
- Pages = THIN composition ONLY (no business logic)
- Logic lives in HOOKS, not components

### File Convention per Feature

```
features/<name>/
  ui/           # React components
  model/
    types.ts    # THE CONTRACT - define types first
    hooks.ts    # All logic here (not in components)
  api/          # API calls (use shared/api client)
  index.ts      # Public API only
```

### Non-Negotiables

- All interactive elements MUST have `data-testid` attributes
- Accessibility: semantic HTML, ARIA labels, keyboard navigation
- Types-first: `model/types.ts` is the contract, implement against it
- Every feature needs unit tests + Storybook stories

### Quality Gates

```bash
npm run build && npm run lint
npx eslint src/ --rule 'import/no-restricted-paths: error'
```

Full pattern reference: `~/.claude/patterns/frontend-fsd/`
Audit tool: `~/.claude/patterns/frontend-fsd/fsd-audit.ts`
ESLint rules: `~/.claude/patterns/frontend-fsd/.eslintrc.cjs`

</fsd-pattern>
