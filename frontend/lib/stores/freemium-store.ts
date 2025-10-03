/**
 * Freemium Store Façade - Backward Compatibility Layer
 *
 * This file is a façade that re-exports the modular freemium store implementation.
 * The actual implementation has been refactored into focused slices under
 * frontend/lib/stores/freemium/ directory.
 *
 * Legacy imports like:
 *     import { useFreemiumStore } from '@/lib/stores/freemium-store'
 *
 * Will continue to work and now resolve to the modular implementation.
 *
 * For new code, you can import directly from the package:
 *     import { useFreemiumStore } from '@/lib/stores/freemium'
 *
 * Migration Status: FAÇADE ACTIVE (Jan 2025)
 * Original monolith: 1,263 lines → Refactored into 8 focused slices
 */

// Re-export everything from the modular implementation
export * from './freemium/index';

// Explicitly re-export main exports for clarity
export {
  useFreemiumStore,
  useFreemiumSession,
  useFreemiumProgress,
  useFreemiumConversion,
  createFreemiumStore,
  selectIsSessionExpired,
  selectCanStartAssessment,
  selectHasValidSession,
  selectResponseCount,
} from './freemium/index';

// Re-export default (base store) for backward compatibility
export { default } from './freemium/index';

// Re-export types for convenience
export type {
  FreemiumStore,
  FreemiumStoreState,
  FreemiumStoreActions,
  FreemiumStoreComputed,
} from './freemium/index';
