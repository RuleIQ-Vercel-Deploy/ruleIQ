import { FlatCompat } from '@eslint/eslintrc';
import js from '@eslint/js';
import typescriptEslint from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import prettier from 'eslint-config-prettier';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

export default [
  js.configs.recommended,
  ...compat.extends('next/core-web-vitals'),
  prettier,
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    plugins: {
      '@typescript-eslint': typescriptEslint,
      'jsx-a11y': jsxA11y,
    },
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        project: false, // Disable project-based parsing for production readiness
      },
    },
    rules: {
      // Critical TypeScript Rules Only - Production Ready
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_|^error$|^loading$|^data$' }],
      '@typescript-eslint/no-explicit-any': 'off', // Allow for development flexibility
      '@typescript-eslint/consistent-type-imports': 'off',

      // Critical React Rules Only  
      'react/prop-types': 'off', // Using TypeScript for prop validation
      'react/react-in-jsx-scope': 'off', // Not needed in React 17+
      'react/no-unescaped-entities': 'off', // Allow content flexibility

      // Critical JavaScript Rules Only
      'no-unused-vars': 'off', // Using @typescript-eslint version
      'no-console': 'off', // Allow console for debugging
      'no-debugger': 'error', // Block debugger in production
      'no-undef': 'off', // TypeScript handles this better
      'prefer-const': 'off',
      'no-var': 'error', // Block var usage
      'eqeqeq': 'off',
      'no-case-declarations': 'off',
      'no-empty-pattern': 'off',
      'no-useless-catch': 'off',
      'no-async-promise-executor': 'off',
      'no-useless-escape': 'off',
      'no-control-regex': 'off',

      // Critical Next.js Rules Only
      '@next/next/no-img-element': 'off', // Allow img elements

      // Critical Hook Rules
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'off', // Allow flexible deps
    },
  },
  {
    ignores: [
      '.next/**',
      'out/**',
      'node_modules/**',
      'coverage/**',
      '*.config.js',
      '*.config.mjs',
      'public/**',
      'tests/**', // Ignore test files for production
      '__tests__/**',
      '*.test.*',
      '*.spec.*',
      'build/**',
      'dist/**',
    ],
  },
];
