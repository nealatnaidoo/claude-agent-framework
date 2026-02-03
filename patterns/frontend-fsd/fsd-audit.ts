#!/usr/bin/env npx tsx
/**
 * Feature-Sliced Design Architecture Auditor
 *
 * Validates that frontend slices follow canonical FSD structure.
 * Run as: npx tsx fsd-audit.ts [src_dir]
 *
 * Exit codes:
 *   0 = All rules passed
 *   1 = Violations found
 */

import fs from 'node:fs';
import path from 'node:path';

interface Violation {
  slice: string;
  rule: string;
  message: string;
}

const LAYERS = ['pages', 'widgets', 'features', 'entities'] as const;

function auditSlice(layer: string, sliceName: string, slicePath: string): Violation[] {
  const violations: Violation[] = [];
  const sliceId = `${layer}/${sliceName}`;

  // ── Must have index.ts ──────────────────────
  const indexFile = path.join(slicePath, 'index.ts');
  const indexTsxFile = path.join(slicePath, 'index.tsx');
  if (!fs.existsSync(indexFile) && !fs.existsSync(indexTsxFile)) {
    violations.push({
      slice: sliceId,
      rule: 'FSD001',
      message: 'Missing index.ts barrel file (public API)',
    });
  }

  // ── Must have model/types.ts (except pages) ────────────────
  const typesFile = path.join(slicePath, 'model', 'types.ts');
  if (!fs.existsSync(typesFile) && layer !== 'pages') {
    violations.push({
      slice: sliceId,
      rule: 'FSD002',
      message: 'Missing model/types.ts — every slice must define its type contract',
    });
  }

  // ── Must have ui/ directory ─────────────────
  const uiDir = path.join(slicePath, 'ui');
  if (!fs.existsSync(uiDir)) {
    violations.push({
      slice: sliceId,
      rule: 'FSD003',
      message: 'Missing ui/ directory',
    });
  } else {
    // Every .tsx in ui/ must have a .test.tsx
    const files = fs.readdirSync(uiDir);
    const components = files.filter(
      (f) => f.endsWith('.tsx') && !f.endsWith('.test.tsx') && !f.endsWith('.stories.tsx')
    );

    for (const comp of components) {
      const testFile = comp.replace('.tsx', '.test.tsx');
      if (!files.includes(testFile)) {
        violations.push({
          slice: sliceId,
          rule: 'FSD004',
          message: `Component ${comp} is missing test file: ${testFile}`,
        });
      }

      // Storybook stories required for non-page components
      if (layer !== 'pages') {
        const storyFile = comp.replace('.tsx', '.stories.tsx');
        if (!files.includes(storyFile)) {
          violations.push({
            slice: sliceId,
            rule: 'FSD005',
            message: `Component ${comp} is missing Storybook story: ${storyFile}`,
          });
        }
      }
    }
  }

  // ── No hooks in page components ─────────────
  if (layer === 'pages' && fs.existsSync(uiDir)) {
    const uiFiles = fs.readdirSync(uiDir).filter(
      (f) => f.endsWith('.tsx') && !f.includes('.test.') && !f.includes('.stories.')
    );

    for (const file of uiFiles) {
      const content = fs.readFileSync(path.join(uiDir, file), 'utf-8');
      // Check for useState, useEffect, useReducer, useMemo — pages should not have these
      if (/\buseState\b|\buseEffect\b|\buseReducer\b|\buseMemo\b/.test(content)) {
        violations.push({
          slice: sliceId,
          rule: 'FSD006',
          message: `Page component ${file} contains hooks — pages must be composition-only`,
        });
      }
    }
  }

  return violations;
}

function auditSharedLayer(sharedPath: string): Violation[] {
  const violations: Violation[] = [];

  // Shared layer required subdirectories
  const requiredDirs = ['ui', 'lib', 'types'];
  for (const dir of requiredDirs) {
    if (!fs.existsSync(path.join(sharedPath, dir))) {
      violations.push({
        slice: 'shared',
        rule: 'FSD007',
        message: `Shared layer missing required directory: ${dir}/`,
      });
    }
  }

  // Check shared/index.ts exists
  if (!fs.existsSync(path.join(sharedPath, 'index.ts'))) {
    violations.push({
      slice: 'shared',
      rule: 'FSD001',
      message: 'Missing shared/index.ts barrel file',
    });
  }

  return violations;
}

function main(): void {
  const srcDir = process.argv[2] ?? 'src';
  const srcPath = path.resolve(srcDir);

  if (!fs.existsSync(srcPath)) {
    console.error(`Directory not found: ${srcPath}`);
    process.exit(1);
  }

  const allViolations: Violation[] = [];

  // Audit each layer
  for (const layer of LAYERS) {
    const layerPath = path.join(srcPath, layer);
    if (!fs.existsSync(layerPath)) continue;

    const slices = fs.readdirSync(layerPath).filter((f) =>
      fs.statSync(path.join(layerPath, f)).isDirectory()
    );

    for (const slice of slices) {
      allViolations.push(...auditSlice(layer, slice, path.join(layerPath, slice)));
    }
  }

  // Audit shared layer
  const sharedPath = path.join(srcPath, 'shared');
  if (fs.existsSync(sharedPath)) {
    allViolations.push(...auditSharedLayer(sharedPath));
  }

  if (allViolations.length > 0) {
    console.error(`\n${'='.repeat(70)}`);
    console.error(`FSD ARCHITECTURE VIOLATIONS: ${allViolations.length} found`);
    console.error(`${'='.repeat(70)}\n`);
    for (const v of allViolations) {
      console.error(`  ${v.rule} | ${v.slice} | ${v.message}`);
    }
    console.error(`\n${'='.repeat(70)}`);
    process.exit(1);
  } else {
    console.log('✓ All FSD architecture rules passed');
  }
}

main();
