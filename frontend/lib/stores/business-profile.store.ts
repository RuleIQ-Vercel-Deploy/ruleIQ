/**
 * Business Profile Store
 * 
 * Zustand store for managing business profile state with:
 * - Draft saving for wizard steps
 * - API integration with field mapping
 * - Validation and error handling
 * - Persistence for draft data
 */

import { create } from 'zustand';
import { persist, createJSONStorage , devtools } from 'zustand/middleware';

import { businessProfileService } from '@/lib/api/business-profiles.service';
import { 
  validateWizardStep, 
  validateCompleteProfile,
  formatValidationErrors 
} from '@/lib/validations/business-profile';
import { 
  type BusinessProfile, 
  type BusinessProfileFormData,
  WizardStepData,
  WIZARD_STEPS,
  type FrameworkRecommendation
} from '@/types/business-profile';

export interface BusinessProfileState {
  // Profile Data
  profile: BusinessProfile | null;
  draftProfile: Partial<BusinessProfileFormData> | null;
  
  // Wizard State
  currentStep: number;
  completedSteps: Set<number>;
  stepValidation: Record<number, boolean>;
  
  // Loading States
  isLoading: boolean;
  isSaving: boolean;
  isValidating: boolean;
  
  // Error Handling
  error: string | null;
  errorType: 'network' | 'validation' | 'permission' | 'timeout' | 'unknown' | null;
  validationErrors: Array<{ field: string; message: string }>;
  retryCount: number;
  
  // Framework Recommendations
  recommendations: FrameworkRecommendation[];
  isLoadingRecommendations: boolean;
  
  // Actions - Profile Management
  loadProfile: () => Promise<void>;
  saveProfile: (data: BusinessProfileFormData) => Promise<void>;
  updateProfile: (updates: Partial<BusinessProfileFormData>) => Promise<void>;
  deleteProfile: () => Promise<void>;
  clearProfile: () => void;
  
  // Actions - Draft Management
  saveDraft: (stepData: Partial<BusinessProfileFormData>) => void;
  loadDraft: () => Partial<BusinessProfileFormData> | null;
  clearDraft: () => void;
  
  // Actions - Wizard Navigation
  setCurrentStep: (step: number) => void;
  nextStep: () => void;
  previousStep: () => void;
  goToStep: (step: number) => void;
  markStepComplete: (step: number) => void;
  
  // Actions - Validation
  validateCurrentStep: () => Promise<boolean>;
  validateAllSteps: () => Promise<boolean>;
  clearValidationErrors: () => void;
  
  // Actions - Framework Recommendations
  loadFrameworkRecommendations: () => Promise<void>;
  
  // Actions - Utility
  reset: () => void;
  clearError: () => void;
}

const initialState = {
  profile: null,
  draftProfile: null,
  currentStep: 0,
  completedSteps: new Set<number>(),
  stepValidation: {},
  isLoading: false,
  isSaving: false,
  isValidating: false,
  error: null,
  errorType: null,
  validationErrors: [],
  retryCount: 0,
  recommendations: [],
  isLoadingRecommendations: false,
};

export const useBusinessProfileStore = create<BusinessProfileState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // Profile Management Actions
        loadProfile: async () => {
          set({ isLoading: true, error: null, errorType: null }, false, 'loadProfile/start');

          try {
            const profile = await businessProfileService.getProfile();
            set({
              profile,
              isLoading: false,
              retryCount: 0,
              // If profile exists, populate draft for editing
              draftProfile: profile ? { ...profile } : null
            }, false, 'loadProfile/success');
          } catch (error: any) {
            const errorType = error.code === 'NETWORK_ERROR' ? 'network' :
                             error.code === 'PERMISSION_DENIED' ? 'permission' :
                             error.code === 'TIMEOUT' ? 'timeout' : 'unknown';

            set({
              error: error.detail || error.message || 'Failed to load profile',
              errorType,
              isLoading: false,
              retryCount: get().retryCount + 1
            }, false, 'loadProfile/error');
          }
        },

        saveProfile: async (data: BusinessProfileFormData) => {
          set({ isSaving: true, error: null, errorType: null, validationErrors: [] }, false, 'saveProfile/start');

          try {
            // Validate complete profile before saving
            const validation = validateCompleteProfile(data);
            if (!validation.success && validation.errors) {
              const errors = formatValidationErrors(validation.errors);
              set({
                validationErrors: errors,
                errorType: 'validation',
                isSaving: false
              }, false, 'saveProfile/validationError');
              throw new Error('Please fix validation errors before saving');
            }

            const savedProfile = await businessProfileService.saveProfile(data);

            set({
              profile: savedProfile,
              draftProfile: null, // Clear draft after successful save
              isSaving: false,
              completedSteps: new Set([0, 1, 2, 3]), // Mark all steps complete
              error: null,
              errorType: null,
              retryCount: 0
            }, false, 'saveProfile/success');

          } catch (error: any) {
            const errorType = error.message?.includes('validation') ? 'validation' :
                             error.code === 'NETWORK_ERROR' ? 'network' :
                             error.code === 'PERMISSION_DENIED' ? 'permission' :
                             error.code === 'TIMEOUT' ? 'timeout' : 'unknown';

            set({
              error: error.detail || error.message || 'Failed to save profile',
              errorType,
              isSaving: false,
              retryCount: get().retryCount + 1
            }, false, 'saveProfile/error');
            throw error;
          }
        },

        updateProfile: async (updates: Partial<BusinessProfileFormData>) => {
          const { profile } = get();
          if (!profile) {
            throw new Error('No existing profile to update');
          }

          set({ isSaving: true, error: null }, false, 'updateProfile/start');
          
          try {
            const updatedProfile = await businessProfileService.updateProfile(profile, updates);
            set({ 
              profile: updatedProfile,
              isSaving: false 
            }, false, 'updateProfile/success');
          } catch (error: any) {
            set({ 
              error: error.detail || error.message || 'Failed to update profile',
              isSaving: false 
            }, false, 'updateProfile/error');
            throw error;
          }
        },

        deleteProfile: async () => {
          set({ isLoading: true, error: null }, false, 'deleteProfile/start');
          
          try {
            await businessProfileService.deleteProfile();
            set({ 
              ...initialState,
              isLoading: false 
            }, false, 'deleteProfile/success');
          } catch (error: any) {
            set({ 
              error: error.detail || error.message || 'Failed to delete profile',
              isLoading: false 
            }, false, 'deleteProfile/error');
            throw error;
          }
        },

        clearProfile: () => {
          set({ 
            profile: null,
            draftProfile: null,
            currentStep: 0,
            completedSteps: new Set<number>(),
            stepValidation: {},
            validationErrors: [],
            error: null,
            errorType: null,
            retryCount: 0
          }, false, 'clearProfile');
        },

        // Draft Management Actions
        saveDraft: (stepData: Partial<BusinessProfileFormData>) => {
          const { draftProfile } = get();
          const updatedDraft = { ...draftProfile, ...stepData };
          set({ draftProfile: updatedDraft }, false, 'saveDraft');
        },

        loadDraft: () => {
          return get().draftProfile;
        },

        clearDraft: () => {
          set({ draftProfile: null }, false, 'clearDraft');
        },

        // Wizard Navigation Actions
        setCurrentStep: (step: number) => {
          if (step >= 0 && step < WIZARD_STEPS.length) {
            set({ currentStep: step }, false, 'setCurrentStep');
          }
        },

        nextStep: () => {
          const { currentStep } = get();
          if (currentStep < WIZARD_STEPS.length - 1) {
            set({ currentStep: currentStep + 1 }, false, 'nextStep');
          }
        },

        previousStep: () => {
          const { currentStep } = get();
          if (currentStep > 0) {
            set({ currentStep: currentStep - 1 }, false, 'previousStep');
          }
        },

        goToStep: (step: number) => {
          if (step >= 0 && step < WIZARD_STEPS.length) {
            set({ currentStep: step }, false, 'goToStep');
          }
        },

        markStepComplete: (step: number) => {
          const { completedSteps } = get();
          const newCompletedSteps = new Set(completedSteps);
          newCompletedSteps.add(step);
          set({ completedSteps: newCompletedSteps }, false, 'markStepComplete');
        },

        // Validation Actions
        validateCurrentStep: async () => {
          const { currentStep, draftProfile } = get();
          const stepId = WIZARD_STEPS[currentStep]?.id;
          
          if (!stepId || !draftProfile) {
            return false;
          }

          set({ isValidating: true, validationErrors: [] }, false, 'validateCurrentStep/start');
          
          try {
            const validation = validateWizardStep(
              stepId as any, 
              draftProfile
            );
            
            if (validation.success) {
              const { stepValidation, completedSteps } = get();
              const newStepValidation = { ...stepValidation, [currentStep]: true };
              const newCompletedSteps = new Set(completedSteps);
              newCompletedSteps.add(currentStep);
              
              set({ 
                stepValidation: newStepValidation,
                completedSteps: newCompletedSteps,
                isValidating: false 
              }, false, 'validateCurrentStep/success');
              return true;
            } else {
              const errors = validation.errors ? formatValidationErrors(validation.errors) : [];
              set({ 
                validationErrors: errors,
                isValidating: false 
              }, false, 'validateCurrentStep/error');
              return false;
            }
          } catch (error: any) {
            set({ 
              error: error.message || 'Validation failed',
              isValidating: false 
            }, false, 'validateCurrentStep/exception');
            return false;
          }
        },

        validateAllSteps: async () => {
          const { draftProfile } = get();
          if (!draftProfile) return false;

          set({ isValidating: true, validationErrors: [] }, false, 'validateAllSteps/start');
          
          try {
            const validation = validateCompleteProfile(draftProfile);
            
            if (validation.success) {
              set({ 
                stepValidation: { 0: true, 1: true, 2: true, 3: true },
                completedSteps: new Set([0, 1, 2, 3]),
                isValidating: false 
              }, false, 'validateAllSteps/success');
              return true;
            } else {
              const errors = validation.errors ? formatValidationErrors(validation.errors) : [];
              set({ 
                validationErrors: errors,
                isValidating: false 
              }, false, 'validateAllSteps/error');
              return false;
            }
          } catch (error: any) {
            set({ 
              error: error.message || 'Validation failed',
              isValidating: false 
            }, false, 'validateAllSteps/exception');
            return false;
          }
        },

        clearValidationErrors: () => {
          set({ validationErrors: [] }, false, 'clearValidationErrors');
        },

        // Framework Recommendations Actions
        loadFrameworkRecommendations: async () => {
          set({ isLoadingRecommendations: true }, false, 'loadRecommendations/start');
          
          try {
            const recommendations = await businessProfileService.getFrameworkRecommendations();
            set({ 
              recommendations,
              isLoadingRecommendations: false 
            }, false, 'loadRecommendations/success');
          } catch (error: any) {
            // Don't set error for recommendations - they're not critical
            console.warn('Failed to load framework recommendations:', error);
            set({ 
              recommendations: [],
              isLoadingRecommendations: false 
            }, false, 'loadRecommendations/error');
          }
        },

        // Utility Actions
        reset: () => {
          set(initialState, false, 'reset');
        },

        clearError: () => {
          set({ error: null }, false, 'clearError');
        },
      }),
      {
        name: "ruleiq-business-profile-storage",
        storage: createJSONStorage(() => localStorage),
        // Only persist draft data and wizard state, not the full profile
        partialize: (state) => ({
          draftProfile: state.draftProfile,
          currentStep: state.currentStep,
          completedSteps: Array.from(state.completedSteps), // Convert Set to Array for serialization
          stepValidation: state.stepValidation,
        }),
        skipHydration: true,
      },
    ),
    {
      name: 'business-profile-store'
    }
  )
);

// Selector hooks for specific state slices
export const useProfileData = () => useBusinessProfileStore(state => state.profile);
export const useDraftData = () => useBusinessProfileStore(state => state.draftProfile);
export const useWizardState = () => useBusinessProfileStore(state => ({
  currentStep: state.currentStep,
  completedSteps: state.completedSteps,
  stepValidation: state.stepValidation,
}));
export const useLoadingState = () => useBusinessProfileStore(state => ({
  isLoading: state.isLoading,
  isSaving: state.isSaving,
  isValidating: state.isValidating,
}));
export const useErrorState = () => useBusinessProfileStore(state => ({
  error: state.error,
  validationErrors: state.validationErrors,
}));