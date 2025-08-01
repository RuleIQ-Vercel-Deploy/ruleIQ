"use client"

import { create } from 'zustand'
import { persist, createJSONStorage , devtools } from 'zustand/middleware'

import { assessmentService, type CreateAssessmentRequest, type UpdateAssessmentRequest, type SubmitAssessmentAnswerRequest } from '@/lib/api/assessments.service'

import type { Assessment, AssessmentQuestion } from '@/types/api'
import type { UnknownRecord } from '@/types/common'

interface AssessmentState {
  // Data
  assessments: Assessment[]
  currentAssessment: Assessment | null
  assessmentQuestions: AssessmentQuestion[]
  assessmentResults: Record<string, unknown> | null
  
  // UI State
  isLoading: boolean
  isCreating: boolean
  isSubmitting: boolean
  isSaving: boolean
  error: string | null
  
  // Pagination
  total: number
  currentPage: number
  pageSize: number
  
  // Filters
  filters: {
    businessProfileId?: string
    frameworkId?: string
    status?: string
  }
  
  // Actions - Assessment Management
  loadAssessments: (_params?: { business_profile_id?: string; framework_id?: string; status?: string; page?: number; page_size?: number }) => Promise<void>
  loadAssessment: (_id: string) => Promise<void>
  createAssessment: (_data: CreateAssessmentRequest) => Promise<Assessment>
  updateAssessment: (_id: string, _data: UpdateAssessmentRequest) => Promise<void>
  deleteAssessment: (_id: string) => Promise<void>
  completeAssessment: (_id: string) => Promise<void>

  // Actions - Questions & Answers
  loadAssessmentQuestions: (_assessmentId: string) => Promise<void>
  submitAnswer: (_assessmentId: string, _data: SubmitAssessmentAnswerRequest) => Promise<void>

  // Actions - Results
  loadAssessmentResults: (_id: string) => Promise<void>

  // Actions - Quick Assessment
  startQuickAssessment: (_businessProfileId: string, _frameworkId: string) => Promise<Record<string, unknown>>

  // Actions - Filters & UI
  setFilters: (_filters: AssessmentState['filters']) => void
  setPage: (_page: number) => void
  clearError: () => void
  reset: () => void
}

const initialState = {
  assessments: [],
  currentAssessment: null,
  assessmentQuestions: [],
  assessmentResults: null,
  isLoading: false,
  isCreating: false,
  isSubmitting: false,
  isSaving: false,
  error: null,
  total: 0,
  currentPage: 1,
  pageSize: 20,
  filters: {},
}

export const useAssessmentStore = create<AssessmentState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Assessment Management
        loadAssessments: async (params) => {
          set({ isLoading: true, error: null }, false, 'loadAssessments/start')
          
          try {
            const { items, total } = await assessmentService.getAssessments({
              ...params,
              page: params?.page || get().currentPage,
              page_size: params?.page_size || get().pageSize,
            })
            
            set({
              assessments: items,
              total,
              isLoading: false,
            }, false, 'loadAssessments/success')
          } catch (error: unknown) {
            set({
              isLoading: false,
              error: (error as UnknownRecord)?.detail || (error as UnknownRecord)?.message || 'Failed to load assessments',
            }, false, 'loadAssessments/error')
          }
        },

        loadAssessment: async (id) => {
          set({ isLoading: true, error: null }, false, 'loadAssessment/start')
          
          try {
            const assessment = await assessmentService.getAssessment(id)
            set({
              currentAssessment: assessment,
              isLoading: false,
            }, false, 'loadAssessment/success')
          } catch (error: unknown) {
            set({
              isLoading: false,
              error: (error as UnknownRecord)?.detail || (error as UnknownRecord)?.message || 'Failed to load assessment',
            }, false, 'loadAssessment/error')
          }
        },

        createAssessment: async (data) => {
          set({ isCreating: true, error: null }, false, 'createAssessment/start')
          
          try {
            const assessment = await assessmentService.createAssessment(data)
            
            set(state => ({
              assessments: [assessment, ...state.assessments],
              currentAssessment: assessment,
              isCreating: false,
            }), false, 'createAssessment/success')
            
            return assessment
          } catch (error: any) {
            set({
              isCreating: false,
              error: error.detail || error.message || 'Failed to create assessment',
            }, false, 'createAssessment/error')
            throw error
          }
        },

        updateAssessment: async (id, data) => {
          set({ isSaving: true, error: null }, false, 'updateAssessment/start')
          
          try {
            const updatedAssessment = await assessmentService.updateAssessment(id, data)
            
            set(state => ({
              assessments: state.assessments.map(a => 
                a.id === id ? updatedAssessment : a
              ),
              currentAssessment: state.currentAssessment?.id === id 
                ? updatedAssessment 
                : state.currentAssessment,
              isSaving: false,
            }), false, 'updateAssessment/success')
          } catch (error: any) {
            set({
              isSaving: false,
              error: error.detail || error.message || 'Failed to update assessment',
            }, false, 'updateAssessment/error')
          }
        },

        deleteAssessment: async (id) => {
          set({ isLoading: true, error: null }, false, 'deleteAssessment/start')
          
          try {
            await assessmentService.deleteAssessment(id)
            
            set(state => ({
              assessments: state.assessments.filter(a => a.id !== id),
              currentAssessment: state.currentAssessment?.id === id 
                ? null 
                : state.currentAssessment,
              isLoading: false,
            }), false, 'deleteAssessment/success')
          } catch (error: any) {
            set({
              isLoading: false,
              error: error.detail || error.message || 'Failed to delete assessment',
            }, false, 'deleteAssessment/error')
          }
        },

        completeAssessment: async (id) => {
          set({ isSubmitting: true, error: null }, false, 'completeAssessment/start')
          
          try {
            const completedAssessment = await assessmentService.completeAssessment(id)
            
            set(state => ({
              assessments: state.assessments.map(a => 
                a.id === id ? completedAssessment : a
              ),
              currentAssessment: state.currentAssessment?.id === id 
                ? completedAssessment 
                : state.currentAssessment,
              isSubmitting: false,
            }), false, 'completeAssessment/success')
          } catch (error: any) {
            set({
              isSubmitting: false,
              error: error.detail || error.message || 'Failed to complete assessment',
            }, false, 'completeAssessment/error')
          }
        },

        // Questions & Answers
        loadAssessmentQuestions: async (assessmentId) => {
          set({ isLoading: true, error: null }, false, 'loadQuestions/start')
          
          try {
            const questions = await assessmentService.getAssessmentQuestions(assessmentId)
            set({
              assessmentQuestions: questions,
              isLoading: false,
            }, false, 'loadQuestions/success')
          } catch (error: any) {
            set({
              isLoading: false,
              error: error.detail || error.message || 'Failed to load questions',
            }, false, 'loadQuestions/error')
          }
        },

        submitAnswer: async (assessmentId, data) => {
          set({ isSubmitting: true, error: null }, false, 'submitAnswer/start')
          
          try {
            await assessmentService.submitAssessmentAnswer(assessmentId, data)
            set({ isSubmitting: false }, false, 'submitAnswer/success')
          } catch (error: any) {
            set({
              isSubmitting: false,
              error: error.detail || error.message || 'Failed to submit answer',
            }, false, 'submitAnswer/error')
          }
        },

        // Results
        loadAssessmentResults: async (id) => {
          set({ isLoading: true, error: null }, false, 'loadResults/start')
          
          try {
            const results = await assessmentService.getAssessmentResults(id)
            set({
              assessmentResults: results,
              isLoading: false,
            }, false, 'loadResults/success')
          } catch (error: any) {
            set({
              isLoading: false,
              error: error.detail || error.message || 'Failed to load results',
            }, false, 'loadResults/error')
          }
        },

        // Quick Assessment
        startQuickAssessment: async (businessProfileId, frameworkId) => {
          set({ isCreating: true, error: null }, false, 'quickAssessment/start')
          
          try {
            const result = await assessmentService.getQuickAssessment(businessProfileId, frameworkId)
            set({ isCreating: false }, false, 'quickAssessment/success')
            return result
          } catch (error: any) {
            set({
              isCreating: false,
              error: error.detail || error.message || 'Failed to start quick assessment',
            }, false, 'quickAssessment/error')
            throw error
          }
        },

        // Filters & UI
        setFilters: (filters) => {
          set({ filters, currentPage: 1 }, false, 'setFilters')
        },

        setPage: (page) => {
          set({ currentPage: page }, false, 'setPage')
        },

        clearError: () => {
          set({ error: null }, false, 'clearError')
        },

        reset: () => {
          set(initialState, false, 'reset')
        },
      }),
      {
        name: 'ruleiq-assessment-storage',
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          // Only persist filters and pagination
          filters: state.filters,
          pageSize: state.pageSize,
        }),
      }
    ),
    {
      name: 'assessment-store',
    }
  )
)

// Selector hooks
export const useAssessments = () => useAssessmentStore(state => state.assessments)
export const useCurrentAssessment = () => useAssessmentStore(state => state.currentAssessment)
export const useAssessmentQuestions = () => useAssessmentStore(state => state.assessmentQuestions)
export const useAssessmentResults = () => useAssessmentStore(state => state.assessmentResults)
export const useAssessmentLoading = () => useAssessmentStore(state => ({
  isLoading: state.isLoading,
  isCreating: state.isCreating,
  isSubmitting: state.isSubmitting,
  isSaving: state.isSaving,
  error: state.error,
}))

// Helper hooks
export const useAssessmentProgress = () => {
  const currentAssessment = useAssessmentStore(state => state.currentAssessment)
  
  if (!currentAssessment) {
    return null
  }
  
  // Calculate progress based on answered questions
  const totalQuestions = currentAssessment.total_questions || 0
  const answeredQuestions = currentAssessment.answered_questions || 0
  const progress = totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0
  
  return {
    totalQuestions,
    answeredQuestions,
    progress,
    isComplete: currentAssessment.status === 'completed',
  }
}