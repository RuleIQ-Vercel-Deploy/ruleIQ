import { describe, it, expect, beforeEach, vi } from 'vitest';

import { businessProfileService } from '@/lib/api/business-profiles.service';
import { useBusinessProfileStore } from '@/lib/stores/business-profile.store';

// Mock the business profile service
vi.mock('@/lib/api/business-profiles.service', () => ({
  businessProfileService: {
    getProfile: vi.fn(),
    saveProfile: vi.fn(),
    updateProfile: vi.fn(),
    deleteProfile: vi.fn(),
  },
}));

describe('Business Profile Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    useBusinessProfileStore.getState().clearProfile();
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const state = useBusinessProfileStore.getState();

      expect(state.profile).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.isComplete).toBe(false);
      expect(state.currentStep).toBe(1);
      expect(state.formData).toEqual({});
    });
  });

  describe('Profile Management', () => {
    const mockProfile = {
      id: '1',
      company_name: 'Test Company',
      industry: 'Technology',
      employee_count: '10-50',
      data_types: ['personal_data'],
      description: 'Test description',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    it('should update form data correctly', () => {
      const { updateFormData } = useBusinessProfileStore.getState();

      updateFormData(mockProfile);

      const state = useBusinessProfileStore.getState();
      expect(state.formData).toEqual(mockProfile);
    });

    it('should clear profile correctly', () => {
      const { setProfile, clearProfile } = useBusinessProfileStore.getState();

      // Set profile first
      setProfile(mockProfile);
      expect(useBusinessProfileStore.getState().profile).toEqual(mockProfile);

      // Clear profile
      clearProfile();

      const state = useBusinessProfileStore.getState();
      expect(state.profile).toBeNull();
      expect(state.isComplete).toBe(false);
      expect(state.formData).toEqual({});
      expect(state.currentStep).toBe(1);
    });

    it('should update profile fields', () => {
      const { setProfile, updateProfile } = useBusinessProfileStore.getState();

      setProfile(mockProfile);

      const updates = {
        company_name: 'Updated Company',
        description: 'Updated description',
      };

      updateProfile(updates);

      const state = useBusinessProfileStore.getState();
      expect(state.profile?.company_name).toBe('Updated Company');
      expect(state.profile?.description).toBe('Updated description');
      expect(state.profile?.industry).toBe('Technology'); // Should preserve other fields
    });
  });

  describe('Loading States', () => {
    it('should set loading state correctly', () => {
      const { setLoading } = useBusinessProfileStore.getState();

      setLoading(true);
      expect(useBusinessProfileStore.getState().isLoading).toBe(true);

      setLoading(false);
      expect(useBusinessProfileStore.getState().isLoading).toBe(false);
    });

    it('should set error state correctly', () => {
      const { setError, clearError } = useBusinessProfileStore.getState();

      setError('Test error');
      expect(useBusinessProfileStore.getState().error).toBe('Test error');

      clearError();
      expect(useBusinessProfileStore.getState().error).toBeNull();
    });
  });

  describe('Form Data Management', () => {
    it('should update form data correctly', () => {
      const { updateFormData } = useBusinessProfileStore.getState();

      const formData = {
        company_name: 'Test Company',
        industry: 'Technology',
      };

      updateFormData(formData);

      const state = useBusinessProfileStore.getState();
      expect(state.formData).toEqual(formData);
    });

    it('should merge form data updates', () => {
      const { updateFormData } = useBusinessProfileStore.getState();

      // Initial data
      updateFormData({
        company_name: 'Test Company',
        industry: 'Technology',
      });

      // Update with additional data
      updateFormData({
        employee_count: '10-50',
        description: 'Test description',
      });

      const state = useBusinessProfileStore.getState();
      expect(state.formData).toEqual({
        company_name: 'Test Company',
        industry: 'Technology',
        employee_count: '10-50',
        description: 'Test description',
      });
    });

    it('should clear form data', () => {
      const { updateFormData, clearFormData } = useBusinessProfileStore.getState();

      updateFormData({
        company_name: 'Test Company',
        industry: 'Technology',
      });

      clearFormData();

      expect(useBusinessProfileStore.getState().formData).toEqual({});
    });
  });

  describe('Wizard Steps', () => {
    it('should navigate to next step', () => {
      const { nextStep } = useBusinessProfileStore.getState();

      expect(useBusinessProfileStore.getState().currentStep).toBe(1);

      nextStep();
      expect(useBusinessProfileStore.getState().currentStep).toBe(2);

      nextStep();
      expect(useBusinessProfileStore.getState().currentStep).toBe(3);
    });

    it('should navigate to previous step', () => {
      const { nextStep, previousStep } = useBusinessProfileStore.getState();

      // Go to step 3
      nextStep();
      nextStep();
      expect(useBusinessProfileStore.getState().currentStep).toBe(3);

      // Go back to step 2
      previousStep();
      expect(useBusinessProfileStore.getState().currentStep).toBe(2);

      // Go back to step 1
      previousStep();
      expect(useBusinessProfileStore.getState().currentStep).toBe(1);
    });

    it('should not go below step 1', () => {
      const { previousStep } = useBusinessProfileStore.getState();

      expect(useBusinessProfileStore.getState().currentStep).toBe(1);

      previousStep();
      expect(useBusinessProfileStore.getState().currentStep).toBe(1);
    });

    it('should set specific step', () => {
      const { setStep } = useBusinessProfileStore.getState();

      setStep(3);
      expect(useBusinessProfileStore.getState().currentStep).toBe(3);

      setStep(1);
      expect(useBusinessProfileStore.getState().currentStep).toBe(1);
    });
  });

  describe('Async Actions', () => {
    const mockProfile = {
      id: '1',
      company_name: 'Test Company',
      industry: 'Technology',
      employee_count: '10-50',
      data_types: ['personal_data'],
      description: 'Test description',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    it('should load profile successfully', async () => {
      vi.mocked(businessProfileService.getProfile).mockResolvedValue(mockProfile);

      const { loadProfile } = useBusinessProfileStore.getState();

      await loadProfile();

      const state = useBusinessProfileStore.getState();
      expect(state.profile).toEqual(mockProfile);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(businessProfileService.getProfile).toHaveBeenCalled();
    });

    it('should handle load profile error', async () => {
      const error = new Error('Failed to load profile');
      vi.mocked(businessProfileService.getProfile).mockRejectedValue(error);

      const { loadProfile } = useBusinessProfileStore.getState();

      await loadProfile();

      const state = useBusinessProfileStore.getState();
      expect(state.profile).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBe('Failed to load profile');
    });

    it('should save profile successfully', async () => {
      const formData = {
        company_name: 'Test Company',
        industry: 'Technology',
        employee_count: '10-50',
        data_types: ['personal_data'],
      };

      vi.mocked(businessProfileService.saveProfile).mockResolvedValue(mockProfile);

      const { updateFormData, saveProfile } = useBusinessProfileStore.getState();

      updateFormData(formData);
      await saveProfile(formData);

      const state = useBusinessProfileStore.getState();
      expect(state.profile).toEqual(mockProfile);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
      expect(businessProfileService.saveProfile).toHaveBeenCalledWith(formData);
    });

    it('should handle save profile error', async () => {
      const formData = {
        company_name: 'Test Company',
        industry: 'Technology',
      };

      const error = new Error('Failed to save profile');
      vi.mocked(businessProfileService.saveProfile).mockRejectedValue(error);

      const { saveProfile } = useBusinessProfileStore.getState();

      await saveProfile(formData);

      const state = useBusinessProfileStore.getState();
      expect(state.profile).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBe('Failed to save profile');
    });
  });

  describe('Computed Properties', () => {
    it('should calculate completion status correctly', () => {
      const { setProfile } = useBusinessProfileStore.getState();

      // No profile - not complete
      expect(useBusinessProfileStore.getState().isComplete).toBe(false);

      // With profile - complete
      setProfile({
        id: '1',
        company_name: 'Test Company',
        industry: 'Technology',
        employee_count: '10-50',
        data_types: ['personal_data'],
        description: 'Test description',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      });

      expect(useBusinessProfileStore.getState().isComplete).toBe(true);
    });

    it('should validate form data completeness', () => {
      const { updateFormData, isFormValid } = useBusinessProfileStore.getState();

      // Empty form - not valid
      expect(isFormValid()).toBe(false);

      // Partial form - not valid
      updateFormData({
        company_name: 'Test Company',
      });
      expect(isFormValid()).toBe(false);

      // Complete form - valid
      updateFormData({
        company_name: 'Test Company',
        industry: 'Technology',
        employee_count: '10-50',
        data_types: ['personal_data'],
      });
      expect(isFormValid()).toBe(true);
    });
  });

  describe('Data Validation', () => {
    it('should validate required fields', () => {
      const { validateStep } = useBusinessProfileStore.getState();

      // Step 1 validation - missing required fields
      expect(validateStep(1, {})).toBe(false);

      // Step 1 validation - with required fields
      expect(validateStep(1, {
        company_name: 'Test Company',
        industry: 'Technology',
        employee_count: '10-50',
      })).toBe(true);

      // Step 2 validation - missing data types
      expect(validateStep(2, {})).toBe(false);

      // Step 2 validation - with data types
      expect(validateStep(2, {
        data_types: ['personal_data'],
      })).toBe(true);
    });

    it('should validate company name format', () => {
      const { validateField } = useBusinessProfileStore.getState();

      expect(validateField('company_name', '')).toBe(false);
      expect(validateField('company_name', 'a')).toBe(false); // Too short
      expect(validateField('company_name', 'Valid Company Name')).toBe(true);
    });

    it('should validate data types selection', () => {
      const { validateField } = useBusinessProfileStore.getState();

      expect(validateField('data_types', [])).toBe(false);
      expect(validateField('data_types', ['personal_data'])).toBe(true);
      expect(validateField('data_types', ['personal_data', 'financial_data'])).toBe(true);
    });
  });
});
