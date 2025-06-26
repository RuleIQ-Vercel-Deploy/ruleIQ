"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useToast } from "@/hooks/use-toast"
import { businessProfileApi, type BusinessProfileCreateInput, type BusinessProfileUpdateInput } from "@/api/business-profiles"
import type { BusinessProfile } from "@/types/api"
import { formatValidationErrors } from "@/lib/utils"

export function useBusinessProfile() {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Get business profile
  const {
    data: profile,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ["business-profile"],
    queryFn: businessProfileApi.get,
    retry: false,
  })

  // Create or update business profile
  const createOrUpdateMutation = useMutation({
    mutationFn: businessProfileApi.createOrUpdate,
    onSuccess: (data) => {
      toast({
        title: "Success",
        description: "Business profile saved successfully",
      })
      queryClient.setQueryData(["business-profile"], data)
      queryClient.invalidateQueries({ queryKey: ["business-profile"] })
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: formatValidationErrors(error),
        variant: "destructive",
      })
    },
  })

  // Update business profile
  const updateMutation = useMutation({
    mutationFn: businessProfileApi.update,
    onSuccess: (data) => {
      toast({
        title: "Success",
        description: "Business profile updated successfully",
      })
      queryClient.setQueryData(["business-profile"], data)
      queryClient.invalidateQueries({ queryKey: ["business-profile"] })
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: formatValidationErrors(error),
        variant: "destructive",
      })
    },
  })

  // Delete business profile
  const deleteMutation = useMutation({
    mutationFn: (profileId: string) => businessProfileApi.delete(profileId),
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Business profile deleted successfully",
      })
      queryClient.removeQueries({ queryKey: ["business-profile"] })
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: formatValidationErrors(error),
        variant: "destructive",
      })
    },
  })

  const createOrUpdate = (data: BusinessProfileCreateInput) => {
    createOrUpdateMutation.mutate(data)
  }

  const update = (data: BusinessProfileUpdateInput) => {
    updateMutation.mutate(data)
  }

  const deleteProfile = (profileId: string) => {
    deleteMutation.mutate(profileId)
  }

  return {
    // Data
    profile,
    isLoading,
    error,
    
    // Actions
    createOrUpdate,
    update,
    deleteProfile,
    refetch,
    
    // Mutation states
    isCreating: createOrUpdateMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    
    // Computed properties
    hasProfile: !!profile,
    isProfileComplete: profile ? calculateCompletionPercentage(profile) === 100 : false,
  }
}

// Helper function to calculate profile completion percentage
function calculateCompletionPercentage(profile: BusinessProfile): number {
  const fields = [
    profile.company_name,
    profile.industry,
    profile.employee_count,
    profile.country,
    profile.annual_revenue,
    profile.data_sensitivity,
    profile.cloud_providers?.length,
    profile.saas_tools?.length,
    profile.existing_frameworks?.length || profile.planned_frameworks?.length,
    profile.compliance_timeline,
  ]

  const completedFields = fields.filter(field => 
    field !== undefined && field !== null && field !== "" && field !== 0
  ).length

  return Math.round((completedFields / fields.length) * 100)
}

// Hook for getting business profile by ID
export function useBusinessProfileById(profileId: string) {
  const { toast } = useToast()

  return useQuery({
    queryKey: ["business-profile", profileId],
    queryFn: () => businessProfileApi.getById(profileId),
    enabled: !!profileId,
    retry: false,
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to load business profile",
        variant: "destructive",
      })
    },
  })
}
