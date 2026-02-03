/**
 * Frontend Feature-Sliced Design - ESLint Configuration
 * Copy to project root
 *
 * @type {import('eslint').Linter.Config}
 */
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: { jsx: true },
    project: './tsconfig.json',
  },
  plugins: [
    '@typescript-eslint',
    'react',
    'react-hooks',
    'jsx-a11y',
    'testing-library',
    'jest-dom',
    'import',
    'boundaries',     // KEY PLUGIN: enforces FSD layer boundaries
    'storybook',
  ],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/strict',
    'plugin:testing-library/react',
    'plugin:jest-dom/recommended',
    'plugin:storybook/recommended',
    'plugin:import/typescript',
  ],
  settings: {
    react: { version: 'detect' },
    'import/resolver': {
      typescript: { alwaysTryTypes: true },
    },
    // ══════════════════════════════════════════
    // BOUNDARIES PLUGIN — FSD LAYER DEFINITIONS
    // ══════════════════════════════════════════
    'boundaries/elements': [
      { type: 'app',      pattern: 'src/app/*' },
      { type: 'pages',    pattern: 'src/pages/*' },
      { type: 'widgets',  pattern: 'src/widgets/*' },
      { type: 'features', pattern: 'src/features/*' },
      { type: 'entities', pattern: 'src/entities/*' },
      { type: 'shared',   pattern: 'src/shared/*' },
    ],
    'boundaries/ignore': ['**/*.test.*', '**/*.stories.*', '**/*.spec.*'],
  },
  rules: {
    // ══════════════════════════════════════════
    // FSD BOUNDARY ENFORCEMENT (NON-NEGOTIABLE)
    // ══════════════════════════════════════════
    'boundaries/element-types': ['error', {
      default: 'disallow',
      rules: [
        // app can import everything below
        { from: 'app',      allow: ['pages', 'widgets', 'features', 'entities', 'shared'] },
        // pages can import widgets, features, entities, shared
        { from: 'pages',    allow: ['widgets', 'features', 'entities', 'shared'] },
        // widgets can import features, entities, shared
        { from: 'widgets',  allow: ['features', 'entities', 'shared'] },
        // features can import entities, shared
        { from: 'features', allow: ['entities', 'shared'] },
        // entities can import shared only
        { from: 'entities', allow: ['shared'] },
        // shared cannot import any layer
        { from: 'shared',   allow: [] },
      ],
    }],

    // PROHIBIT same-layer cross-slice imports
    'boundaries/entry-point': ['error', {
      default: 'disallow',
      rules: [
        // All imports must go through index.ts
        { target: ['pages', 'widgets', 'features', 'entities', 'shared'], allow: 'index.(ts|tsx)' },
      ],
    }],

    // ══════════════════════════════════════════
    // IMPORT HYGIENE
    // ══════════════════════════════════════════
    'import/order': ['error', {
      groups: [
        'builtin',
        'external',
        'internal',
        ['parent', 'sibling', 'index'],
      ],
      pathGroups: [
        { pattern: 'react',           group: 'builtin',  position: 'before' },
        { pattern: '@/app/**',        group: 'internal', position: 'before' },
        { pattern: '@/pages/**',      group: 'internal', position: 'before' },
        { pattern: '@/widgets/**',    group: 'internal', position: 'before' },
        { pattern: '@/features/**',   group: 'internal', position: 'before' },
        { pattern: '@/entities/**',   group: 'internal', position: 'before' },
        { pattern: '@/shared/**',     group: 'internal', position: 'after'  },
      ],
      'newlines-between': 'always',
      alphabetize: { order: 'asc' },
    }],
    'import/no-cycle': 'error',
    'import/no-self-import': 'error',
    'import/no-useless-path-segments': 'error',

    // ══════════════════════════════════════════
    // TYPESCRIPT STRICTNESS
    // ══════════════════════════════════════════
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/explicit-function-return-type': ['warn', {
      allowExpressions: true,
      allowTypedFunctionExpressions: true,
    }],
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/strict-boolean-expressions': 'error',

    // ══════════════════════════════════════════
    // REACT BEST PRACTICES
    // ══════════════════════════════════════════
    'react/prop-types': 'off',               // Using TypeScript
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    'react/jsx-no-leaked-render': 'error',    // Prevent 0/false rendering

    // ══════════════════════════════════════════
    // ACCESSIBILITY (NON-NEGOTIABLE)
    // ══════════════════════════════════════════
    'jsx-a11y/anchor-is-valid': 'error',
    'jsx-a11y/click-events-have-key-events': 'error',
    'jsx-a11y/no-static-element-interactions': 'error',
    'jsx-a11y/aria-props': 'error',

    // ══════════════════════════════════════════
    // TESTING ENFORCEMENT
    // ══════════════════════════════════════════
    'testing-library/prefer-screen-queries': 'error',
    'testing-library/no-wait-for-multiple-assertions': 'error',
    'testing-library/prefer-user-event': 'error',
    'testing-library/no-node-access': 'error',
  },
  overrides: [
    {
      files: ['**/*.test.tsx', '**/*.test.ts', '**/*.spec.tsx', '**/*.spec.ts'],
      rules: {
        '@typescript-eslint/no-explicit-any': 'off',
      },
    },
  ],
};
