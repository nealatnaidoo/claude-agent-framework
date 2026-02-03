# Frontend Feature-Sliced Design Pattern

## Overview

This pattern enforces Feature-Sliced Design (FSD) for all frontend React/TypeScript code. The layer hierarchy is sacred. Import direction flows downward only. Every slice follows the same internal structure.

## Layer Hierarchy (FIXED)

```
src/
  app/              # Layer 7 — Application shell
  │                 #   Providers, routing, global styles, composition root
  │                 #   May import from: ALL layers below
  │
  pages/            # Layer 6 — Full route pages
  │                 #   Compose widgets and features into route-level views
  │                 #   May import from: widgets, features, entities, shared
  │
  widgets/          # Layer 5 — Composite UI blocks
  │                 #   Self-contained UI sections (header, sidebar, data table)
  │                 #   May import from: features, entities, shared
  │
  features/         # Layer 4 — User interactions
  │                 #   Business-meaningful user actions (login, add-to-cart)
  │                 #   May import from: entities, shared
  │
  entities/         # Layer 3 — Business objects
  │                 #   Domain models with UI representation (User, Product)
  │                 #   May import from: shared
  │
  shared/           # Layer 2 — Reusable foundation
                    #   UI kit, utilities, types, constants, API client
                    #   May import from: NOTHING (base layer)
```

## Slice Internal Structure

```
<slice-name>/
  ui/                 # React components — presentational only
    <Component>.tsx
    <Component>.test.tsx
    <Component>.stories.tsx
    <Component>.module.css
  model/              # State management, types, business logic
    types.ts          # TypeScript interfaces — THE CONTRACT
    store.ts          # State (Zustand, context)
    hooks.ts          # Custom hooks encapsulating logic
    selectors.ts      # Derived state (optional)
  api/                # Data fetching
    queries.ts        # React Query / SWR queries
    mutations.ts      # Mutation definitions
    dto.ts            # API shape (separate from domain types)
  lib/                # Pure utility functions
    helpers.ts
    constants.ts
    validators.ts
  index.ts            # PUBLIC API — barrel file
```

## Import Rules (INVIOLABLE)

```
ALLOWED:
  app/       → pages, widgets, features, entities, shared
  pages/     → widgets, features, entities, shared
  widgets/   → features, entities, shared
  features/  → entities, shared
  entities/  → shared
  shared/    → external packages ONLY

FORBIDDEN:
  shared/    → entities, features, widgets, pages, app
  entities/  → features, widgets, pages, app
  features/  → widgets, pages, app
  widgets/   → pages, app
  pages/     → app
  ANY slice  → another slice's internal modules (use index.ts only)
  ANY slice  → sibling slice within same layer
```

## Files Included

| File | Purpose |
|------|---------|
| `.eslintrc.cjs` | ESLint with boundaries plugin for FSD enforcement |
| `fsd-audit.ts` | Structure validation script |

## Usage

1. Copy configuration files to your project root
2. Install dependencies:
   ```bash
   npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin \
     eslint-plugin-boundaries eslint-plugin-import eslint-plugin-react \
     eslint-plugin-react-hooks eslint-plugin-jsx-a11y eslint-plugin-testing-library \
     eslint-plugin-jest-dom eslint-plugin-storybook
   ```
3. Run quality gates:
   ```bash
   npm run lint
   npm run typecheck
   npx tsx fsd-audit.ts src/
   npm run test:coverage
   ```

## Violation Codes

| Code | Rule |
|------|------|
| FSD001 | Missing index.ts barrel file |
| FSD002 | Missing model/types.ts |
| FSD003 | Missing ui/ directory |
| FSD004 | Component missing test file |
| FSD005 | Component missing Storybook story |
| FSD006 | Page component contains hooks |
| FSD007 | Shared layer missing required directory |

## Component Pattern

```typescript
// model/hooks.ts — ALL logic lives here
export function useLoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const loginMutation = useLoginMutation();

  const handleSubmit = async () => {
    await loginMutation.mutateAsync({ email, password });
  };

  return { email, setEmail, password, setPassword, handleSubmit, isLoading: loginMutation.isPending };
}

// ui/LoginForm.tsx — PURE presentation
export function LoginForm() {
  const { email, setEmail, password, setPassword, handleSubmit, isLoading } = useLoginForm();
  return (
    <form onSubmit={handleSubmit}>
      <Input value={email} onChange={setEmail} label="Email" />
      <Input value={password} onChange={setPassword} label="Password" type="password" />
      <Button type="submit" loading={isLoading}>Sign In</Button>
    </form>
  );
}
```
