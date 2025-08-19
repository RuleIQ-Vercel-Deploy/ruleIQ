'use client';

import { create } from 'zustand';
import { persist, createJSONStorage, devtools } from 'zustand/middleware';

import {
  evidenceService,
  type CreateEvidenceRequest,
  type UpdateEvidenceRequest,
  type BulkUpdateEvidenceRequest,
  type EvidenceSearchParams,
  type EvidenceAutomationConfig,
} from '@/lib/api/evidence.service';

import { EvidenceArraySchema, LoadingStateSchema, safeValidate } from './schemas';

import type { EvidenceItem } from '@/types/api';

interface EvidenceState {
  // Data
  evidence: EvidenceItem[];
  currentEvidence: EvidenceItem | null;
  evidenceRequirements: any | null;
  evidenceDashboard: any | null;
  selectedItems: string[];

  // UI State
  isLoading: boolean;
  isUploading: boolean;
  isBulkUpdating: boolean;
  uploadProgress: number;
  error: string | null;

  // Pagination
  total: number;
  currentPage: number;
  pageSize: number;

  // Filters & Sorting
  filters: EvidenceSearchParams;
  searchQuery: string;

  // Actions - Evidence Management
  loadEvidence: (params?: EvidenceSearchParams) => Promise<void>;
  loadEvidenceItem: (id: string) => Promise<void>;
  createEvidence: (data: CreateEvidenceRequest) => Promise<EvidenceItem>;
  updateEvidence: (id: string, data: UpdateEvidenceRequest) => Promise<void>;
  deleteEvidence: (id: string) => Promise<void>;
  bulkUpdateEvidence: (data: BulkUpdateEvidenceRequest) => Promise<void>;

  // Actions - File Upload
  uploadFile: (id: string, file: File) => Promise<void>;

  // Actions - Automation
  configureAutomation: (id: string, config: EvidenceAutomationConfig) => Promise<any>;

  // Actions - Dashboard & Requirements
  loadEvidenceDashboard: (frameworkId: string) => Promise<void>;
  loadEvidenceRequirements: (frameworkId: string) => Promise<void>;

  // Actions - AI Features
  classifyEvidence: (id: string, forceReclassify?: boolean) => Promise<any>;
  analyzeEvidenceQuality: (id: string) => Promise<any>;

  // Actions - Search
  searchEvidence: (query: string) => Promise<void>;

  // Actions - Selection
  selectItem: (id: string) => void;
  deselectItem: (id: string) => void;
  selectAll: () => void;
  clearSelection: () => void;

  // Actions - Data Management
  setEvidence: (evidence: EvidenceItem[]) => void;
  setLoading: (loading: boolean) => void;

  // Actions - Filters & UI
  setFilters: (filters: EvidenceSearchParams) => void;
  setPage: (page: number) => void;
  setSearchQuery: (query: string) => void;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  evidence: [],
  currentEvidence: null,
  evidenceRequirements: null,
  evidenceDashboard: null,
  selectedItems: [],
  isLoading: false,
  isUploading: false,
  isBulkUpdating: false,
  uploadProgress: 0,
  error: null,
  total: 0,
  currentPage: 1,
  pageSize: 20,
  filters: {},
  searchQuery: '',
};

export const useEvidenceStore = create<EvidenceState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Evidence Management
        loadEvidence: async (params) => {
          set({ isLoading: true, error: null }, false, 'loadEvidence/start');

          try {
            const { items, total } = await evidenceService.getEvidence({
              ...get().filters,
              ...params,
              page: params?.page || get().currentPage,
              page_size: params?.page_size || get().pageSize,
            });

            set(
              {
                evidence: items,
                total,
                isLoading: false,
              },
              false,
              'loadEvidence/success',
            );
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to load evidence',
              },
              false,
              'loadEvidence/error',
            );
          }
        },

        loadEvidenceItem: async (id) => {
          set({ isLoading: true, error: null }, false, 'loadEvidenceItem/start');

          try {
            const item = await evidenceService.getEvidenceItem(id);
            set(
              {
                currentEvidence: item,
                isLoading: false,
              },
              false,
              'loadEvidenceItem/success',
            );
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to load evidence item',
              },
              false,
              'loadEvidenceItem/error',
            );
          }
        },

        createEvidence: async (data) => {
          set({ isLoading: true, error: null }, false, 'createEvidence/start');

          try {
            const item = await evidenceService.createEvidence(data);

            set(
              (state) => ({
                evidence: [item, ...state.evidence],
                total: state.total + 1,
                isLoading: false,
              }),
              false,
              'createEvidence/success',
            );

            return item;
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to create evidence',
              },
              false,
              'createEvidence/error',
            );
            throw error;
          }
        },

        updateEvidence: async (id, data) => {
          set({ isLoading: true, error: null }, false, 'updateEvidence/start');

          try {
            const updatedItem = await evidenceService.updateEvidence(id, data);

            set(
              (state) => ({
                evidence: state.evidence.map((e) => (e.id === id ? updatedItem : e)),
                currentEvidence:
                  state.currentEvidence?.id === id ? updatedItem : state.currentEvidence,
                isLoading: false,
              }),
              false,
              'updateEvidence/success',
            );
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to update evidence',
              },
              false,
              'updateEvidence/error',
            );
          }
        },

        deleteEvidence: async (id) => {
          set({ isLoading: true, error: null }, false, 'deleteEvidence/start');

          try {
            await evidenceService.deleteEvidence(id);

            set(
              (state) => ({
                evidence: state.evidence.filter((e) => e.id !== id),
                currentEvidence: state.currentEvidence?.id === id ? null : state.currentEvidence,
                selectedItems: state.selectedItems.filter((itemId) => itemId !== id),
                total: state.total - 1,
                isLoading: false,
              }),
              false,
              'deleteEvidence/success',
            );
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to delete evidence',
              },
              false,
              'deleteEvidence/error',
            );
          }
        },

        bulkUpdateEvidence: async (data) => {
          set({ isBulkUpdating: true, error: null }, false, 'bulkUpdate/start');

          try {
            await evidenceService.bulkUpdateEvidence(data);

            // Reload evidence to reflect changes
            await get().loadEvidence();

            set(
              {
                isBulkUpdating: false,
                selectedItems: [],
              },
              false,
              'bulkUpdate/success',
            );
          } catch (error: any) {
            set(
              {
                isBulkUpdating: false,
                error: error.detail || error.message || 'Failed to bulk update evidence',
              },
              false,
              'bulkUpdate/error',
            );
          }
        },

        // File Upload
        uploadFile: async (id, file) => {
          set({ isUploading: true, uploadProgress: 0, error: null }, false, 'upload/start');

          try {
            const updatedItem = await evidenceService.uploadEvidenceFile(id, file, (progress) => {
              set({ uploadProgress: progress }, false, 'upload/progress');
            });

            set(
              (state) => ({
                evidence: state.evidence.map((e) => (e.id === id ? updatedItem : e)),
                currentEvidence:
                  state.currentEvidence?.id === id ? updatedItem : state.currentEvidence,
                isUploading: false,
                uploadProgress: 0,
              }),
              false,
              'upload/success',
            );
          } catch (error: any) {
            set(
              {
                isUploading: false,
                uploadProgress: 0,
                error: error.detail || error.message || 'Failed to upload file',
              },
              false,
              'upload/error',
            );
          }
        },

        // Automation
        configureAutomation: async (id, config) => {
          set({ isLoading: true, error: null }, false, 'automation/start');

          try {
            const result = await evidenceService.configureEvidenceAutomation(id, config);
            set({ isLoading: false }, false, 'automation/success');
            return result;
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to configure automation',
              },
              false,
              'automation/error',
            );
            throw error;
          }
        },

        // Dashboard & Requirements
        loadEvidenceDashboard: async (frameworkId) => {
          set({ isLoading: true, error: null }, false, 'dashboard/start');

          try {
            const dashboard = await evidenceService.getEvidenceDashboard(frameworkId);
            set(
              {
                evidenceDashboard: dashboard,
                isLoading: false,
              },
              false,
              'dashboard/success',
            );
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to load dashboard',
              },
              false,
              'dashboard/error',
            );
          }
        },

        loadEvidenceRequirements: async (frameworkId) => {
          set({ isLoading: true, error: null }, false, 'requirements/start');

          try {
            const requirements = await evidenceService.getEvidenceRequirements(frameworkId);
            set(
              {
                evidenceRequirements: requirements,
                isLoading: false,
              },
              false,
              'requirements/success',
            );
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to load requirements',
              },
              false,
              'requirements/error',
            );
          }
        },

        // AI Features
        classifyEvidence: async (id, forceReclassify) => {
          set({ isLoading: true, error: null }, false, 'classify/start');

          try {
            const result = await evidenceService.classifyEvidence(id, {
              force_reclassify: forceReclassify,
            });
            set({ isLoading: false }, false, 'classify/success');
            return result;
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to classify evidence',
              },
              false,
              'classify/error',
            );
            throw error;
          }
        },

        analyzeEvidenceQuality: async (id) => {
          set({ isLoading: true, error: null }, false, 'quality/start');

          try {
            const result = await evidenceService.getEvidenceQualityAnalysis(id);
            set({ isLoading: false }, false, 'quality/success');
            return result;
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to analyze quality',
              },
              false,
              'quality/error',
            );
            throw error;
          }
        },

        // Search
        searchEvidence: async (query) => {
          set({ isLoading: true, error: null, searchQuery: query }, false, 'search/start');

          try {
            const results = await evidenceService.searchEvidence(query);
            set(
              {
                evidence: results,
                total: results.length,
                isLoading: false,
              },
              false,
              'search/success',
            );
          } catch (error: any) {
            set(
              {
                isLoading: false,
                error: error.detail || error.message || 'Failed to search evidence',
              },
              false,
              'search/error',
            );
          }
        },

        // Selection
        selectItem: (id) => {
          set(
            (state) => ({
              selectedItems: [...state.selectedItems, id],
            }),
            false,
            'selectItem',
          );
        },

        deselectItem: (id) => {
          set(
            (state) => ({
              selectedItems: state.selectedItems.filter((itemId) => itemId !== id),
            }),
            false,
            'deselectItem',
          );
        },

        selectAll: () => {
          set(
            (state) => ({
              selectedItems: state.evidence.map((e) => e.id),
            }),
            false,
            'selectAll',
          );
        },

        clearSelection: () => {
          set({ selectedItems: [] }, false, 'clearSelection');
        },

        // Filters & UI
        setFilters: (filters) => {
          set({ filters, currentPage: 1 }, false, 'setFilters');
        },

        setPage: (page) => {
          set({ currentPage: page }, false, 'setPage');
        },

        setSearchQuery: (query) => {
          set({ searchQuery: query }, false, 'setSearchQuery');
        },

        // Data Management
        setEvidence: (evidence) => {
          // Map API evidence data to EvidenceItem interface with all required fields
          const mappedEvidence = evidence.map((item: any): EvidenceItem => ({
            id: item.id || '',
            title: item.title || '',
            description: item.description || '', // Ensure always string, never undefined
            control_id: item.control_id || item.controlId || '',
            framework_id: item.framework_id || '',
            business_profile_id: item.business_profile_id || '',
            evidence_type: item.evidence_type || 'manual',
            source: item.source || 'manual',
            tags: item.tags || [],
            status: item.status || 'pending',
            created_at: item.created_at || new Date().toISOString(),
            updated_at: item.updated_at || new Date().toISOString(),
            // Optional fields can be undefined
            quality_score: item.quality_score,
            metadata: item.metadata,
            file_url: item.file_url,
            file_name: item.file_name,
            file_size: item.file_size
          }));
          set({ evidence: mappedEvidence }, false, 'setEvidence');
        },

        setLoading: (loading) => {
          const validatedLoading = safeValidate(LoadingStateSchema, loading, 'setLoading');
          set({ isLoading: validatedLoading }, false, 'setLoading');
        },

        clearError: () => {
          set({ error: null }, false, 'clearError');
        },

        reset: () => {
          set(initialState, false, 'reset');
        },
      }),
      {
        name: 'ruleiq-evidence-storage',
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          // Only persist filters and pagination
          filters: state.filters,
          pageSize: state.pageSize,
        }),
      },
    ),
    {
      name: 'evidence-store',
    },
  ),
);

// Selector hooks
export const useEvidence = () => useEvidenceStore((state) => state.evidence);
export const useCurrentEvidence = () => useEvidenceStore((state) => state.currentEvidence);
export const useSelectedEvidence = () => useEvidenceStore((state) => state.selectedItems);
export const useEvidenceDashboard = () => useEvidenceStore((state) => state.evidenceDashboard);
export const useEvidenceRequirements = () =>
  useEvidenceStore((state) => state.evidenceRequirements);
export const useEvidenceLoading = () =>
  useEvidenceStore((state) => ({
    isLoading: state.isLoading,
    isUploading: state.isUploading,
    isBulkUpdating: state.isBulkUpdating,
    uploadProgress: state.uploadProgress,
    error: state.error,
  }));

// Helper hooks
export const useEvidenceStats = () => {
  const dashboard = useEvidenceStore((state) => state.evidenceDashboard);

  if (!dashboard) {
    return null;
  }

  return {
    totalControls: dashboard.total_controls,
    coveredControls: dashboard.covered_controls,
    pendingEvidence: dashboard.pending_evidence,
    approvedEvidence: dashboard.approved_evidence,
    coveragePercentage: dashboard.coverage_percentage,
    byType: dashboard.by_type,
  };
};
