'use client';

import { create } from 'zustand';
import { persist, createJSONStorage, devtools } from 'zustand/middleware';

import { evidenceCollectionService, type CollectionPlanSummary } from '@/lib/api/evidence-collection.service';

import type { EvidenceCollectionPlan, EvidenceTask } from '@/types/api';

interface EvidenceCollectionState {
  // Collection Plans
  plans: CollectionPlanSummary[];
  currentPlan: EvidenceCollectionPlan | null;
  priorityTasks: EvidenceTask[];

  // UI State
  isLoading: boolean;
  isCreatingPlan: boolean;
  isUpdatingTask: boolean;
  error: string | null;

  // Filters and Sorting
  taskFilters: {
    priority?: string[];
    status?: string[];
    automationLevel?: string[];
    evidenceType?: string[];
  };
  taskSortBy: 'priority' | 'dueDate' | 'effort' | 'status';
  taskSortOrder: 'asc' | 'desc';

  // Actions - Plan Management
  createPlan: (framework: string, targetWeeks?: number) => Promise<EvidenceCollectionPlan>;
  loadPlan: (planId: string) => Promise<void>;
  loadPlans: (framework?: string, status?: string) => Promise<void>;
  refreshCurrentPlan: () => Promise<void>;

  // Actions - Task Management
  loadPriorityTasks: (planId: string, limit?: number) => Promise<void>;
  updateTaskStatus: (taskId: string, status: string, notes?: string) => Promise<void>;

  // Actions - Filtering and Sorting
  setTaskFilters: (filters: EvidenceCollectionState['taskFilters']) => void;
  setTaskSort: (
    sortBy: EvidenceCollectionState['taskSortBy'],
    order?: EvidenceCollectionState['taskSortOrder'],
  ) => void;
  getFilteredAndSortedTasks: () => EvidenceTask[];

  // Actions - UI
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  plans: [],
  currentPlan: null,
  priorityTasks: [],
  isLoading: false,
  isCreatingPlan: false,
  isUpdatingTask: false,
  error: null,
  taskFilters: {},
  taskSortBy: 'priority' as const,
  taskSortOrder: 'asc' as const,
};

export const useEvidenceCollectionStore = create<EvidenceCollectionState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Plan Management Actions
        createPlan: async (framework: string, targetWeeks?: number) => {
          set({ isCreatingPlan: true, error: null }, false, 'createPlan/start');

          try {
            const plan = await evidenceCollectionService.createCollectionPlan({
              framework,
              target_completion_weeks: targetWeeks,
              include_existing_evidence: true,
            });

            set(
              (state) => ({
                ...state,
                currentPlan: plan,
                plans: [
                  ...state.plans,
                  {
                    id: plan.plan_id,
                    framework: plan.framework,
                    status: 'pending',
                    progress_percentage: 0,
                    total_tasks: plan.total_tasks,
                    completed_tasks: 0,
                    estimated_total_hours: plan.estimated_total_hours,
                    completion_target_date: plan.completion_target_date,
                    created_at: plan.created_at,
                  } as CollectionPlanSummary,
                ],
                isCreatingPlan: false,
              }),
              false,
              'createPlan/success',
            );

            return plan;
          } catch (error: unknown) {
            set(
              {
                isCreatingPlan: false,
                error: 
                  error && typeof error === 'object' && 'detail' in error
                    ? (error as any).detail
                    : error && typeof error === 'object' && 'message' in error
                      ? (error as any).message
                      : 'Failed to create collection plan',
              },
              false,
              'createPlan/error',
            );
            throw error;
          }
        },

        loadPlan: async (planId: string) => {
          set({ isLoading: true, error: null }, false, 'loadPlan/start');

          try {
            const plan = await evidenceCollectionService.getCollectionPlan(planId);
            set(
              {
                currentPlan: plan,
                isLoading: false,
              },
              false,
              'loadPlan/success',
            );
          } catch (error: unknown) {
            set(
              {
                isLoading: false,
                error: 
                  error && typeof error === 'object' && 'detail' in error
                    ? (error as any).detail
                    : error && typeof error === 'object' && 'message' in error
                      ? (error as any).message
                      : 'Failed to load collection plan',
              },
              false,
              'loadPlan/error',
            );
          }
        },

        loadPlans: async (framework?: string, status?: string) => {
          set({ isLoading: true, error: null }, false, 'loadPlans/start');

          try {
            const plans = await evidenceCollectionService.listCollectionPlans({
              framework,
              status,
            });
            set(
              {
                plans,
                isLoading: false,
              },
              false,
              'loadPlans/success',
            );
          } catch (error: unknown) {
            set(
              {
                isLoading: false,
                error: 
                  error && typeof error === 'object' && 'detail' in error
                    ? (error as any).detail
                    : error && typeof error === 'object' && 'message' in error
                      ? (error as any).message
                      : 'Failed to load collection plans',
              },
              false,
              'loadPlans/error',
            );
          }
        },

        refreshCurrentPlan: async () => {
          const { currentPlan } = get();
          if (!currentPlan) return;

          await get().loadPlan(currentPlan.plan_id);
        },

        // Task Management Actions
        loadPriorityTasks: async (planId: string, limit: number = 5) => {
          set({ isLoading: true, error: null }, false, 'loadPriorityTasks/start');

          try {
            const tasks = await evidenceCollectionService.getPriorityTasks(planId, limit);
            set(
              {
                priorityTasks: tasks,
                isLoading: false,
              },
              false,
              'loadPriorityTasks/success',
            );
          } catch (error: unknown) {
            set(
              {
                isLoading: false,
                error: 
                  error && typeof error === 'object' && 'detail' in error
                    ? (error as any).detail
                    : error && typeof error === 'object' && 'message' in error
                      ? (error as any).message
                      : 'Failed to load priority tasks',
              },
              false,
              'loadPriorityTasks/error',
            );
          }
        },

        updateTaskStatus: async (taskId: string, status: string, notes?: string) => {
          const { currentPlan } = get();
          if (!currentPlan) return;

          set({ isUpdatingTask: true, error: null }, false, 'updateTaskStatus/start');

          try {
            const updatedTask = await evidenceCollectionService.updateTaskStatus(
              currentPlan.plan_id,
              taskId,
              {
                status: status as any,
                completion_notes: notes,
              },
            );

            // Update task in current plan
            set(
              (state) => ({
                currentPlan: state.currentPlan
                  ? {
                      ...state.currentPlan,
                      tasks: state.currentPlan.tasks.map((task) =>
                        task.task_id === taskId ? updatedTask : task,
                      ),
                    }
                  : null,
                priorityTasks: state.priorityTasks.map((task) =>
                  task.task_id === taskId ? updatedTask : task,
                ),
                isUpdatingTask: false,
              }),
              false,
              'updateTaskStatus/success',
            );

            // Update plan summary if task completed
            if (status === 'completed') {
              set(
                (state) => ({
                  plans: state.plans.map((plan) =>
                    plan.id === currentPlan.plan_id
                      ? { ...plan, completed_tasks: (plan as any).completed_tasks + 1 }
                      : plan,
                  ),
                }),
                false,
                'updateTaskStatus/updateSummary',
              );
            }
          } catch (error: unknown) {
            set(
              {
                isUpdatingTask: false,
                error: 
                  error && typeof error === 'object' && 'detail' in error
                    ? (error as any).detail
                    : error && typeof error === 'object' && 'message' in error
                      ? (error as any).message
                      : 'Failed to update task status',
              },
              false,
              'updateTaskStatus/error',
            );
          }
        },

        // Filtering and Sorting Actions
        setTaskFilters: (filters) => {
          set({ taskFilters: filters }, false, 'setTaskFilters');
        },

        setTaskSort: (sortBy, order = 'asc') => {
          set({ taskSortBy: sortBy, taskSortOrder: order }, false, 'setTaskSort');
        },

        getFilteredAndSortedTasks: () => {
          const { currentPlan, taskFilters, taskSortBy, taskSortOrder } = get();
          if (!currentPlan) return [];

          // Filter tasks
          const filtered = evidenceCollectionService.filterTasks(currentPlan.tasks, taskFilters);

          // Sort tasks
          return evidenceCollectionService.sortTasks(filtered, taskSortBy, taskSortOrder);
        },

        // UI Actions
        clearError: () => {
          set({ error: null }, false, 'clearError');
        },

        reset: () => {
          set(initialState, false, 'reset');
        },
      }),
      {
        name: 'ruleiq-evidence-collection-storage',
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          // Only persist filters and sort preferences
          taskFilters: state.taskFilters,
          taskSortBy: state.taskSortBy,
          taskSortOrder: state.taskSortOrder,
        }),
      },
    ),
    {
      name: 'evidence-collection-store',
    },
  ),
);

// Selector hooks
export const useCollectionPlans = () => useEvidenceCollectionStore((state) => state.plans);
export const useCurrentPlan = () => useEvidenceCollectionStore((state) => state.currentPlan);
export const usePriorityTasks = () => useEvidenceCollectionStore((state) => state.priorityTasks);
export const useCollectionLoading = () =>
  useEvidenceCollectionStore((state) => ({
    isLoading: state.isLoading,
    isCreatingPlan: state.isCreatingPlan,
    isUpdatingTask: state.isUpdatingTask,
    error: state.error,
  }));

// Helper hooks
export const useTaskStatistics = () => {
  const currentPlan = useEvidenceCollectionStore((state) => state.currentPlan);

  if (!currentPlan) {
    return null;
  }

  return evidenceCollectionService.getTaskStatistics(currentPlan);
};

export const useTimeSavings = () => {
  const currentPlan = useEvidenceCollectionStore((state) => state.currentPlan);

  if (!currentPlan) {
    return null;
  }

  return evidenceCollectionService.calculateTimeSavings(currentPlan);
};
