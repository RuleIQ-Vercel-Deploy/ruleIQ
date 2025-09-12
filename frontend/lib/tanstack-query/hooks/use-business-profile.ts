import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { businessProfileService } from '@/lib/api/business-profiles.service';
import { useBusinessProfileStore } from '@/lib/stores/business-profile.store';

import { createQueryKey, type BaseQueryOptions, type BaseMutationOptions } from './base';

// Use the same BusinessProfile type that the service returns
import type { BusinessProfile } from '@/types/business-profile';

// Import types from the service
import type {
  CreateBusinessProfileRequest,
  UpdateBusinessProfileRequest,
} from '@/lib/api/business-profiles.service';

// Query keys
const PROFILE_KEY = 'business-profile';

export const businessProfileKeys = {
  all: [PROFILE_KEY] as const,
  current: () => createQueryKey(PROFILE_KEY, 'current'),
  list: () => createQueryKey(PROFILE_KEY, 'list'),
  detail: (id: string) => createQueryKey(PROFILE_KEY, 'detail', { id }),
  compliance: (id: string) => createQueryKey(PROFILE_KEY, 'compliance', { id }),
};

// Hook to fetch current business profile
export function useCurrentBusinessProfile(options?: BaseQueryOptions<BusinessProfile | null>) {
  const setProfile = useBusinessProfileStore((state) => state.setProfile);

  return useQuery({
    queryKey: businessProfileKeys.current(),
    queryFn: async () => {
      const profile = await businessProfileService.getProfile();
      // Update store with fetched profile if it exists
      if (profile) {
        setProfile(profile);
      }
      return profile;
    },
    ...options,
  });
}

// Hook to fetch all business profiles
export function useBusinessProfiles(options?: BaseQueryOptions<BusinessProfile[]>) {
  return useQuery({
    queryKey: businessProfileKeys.list(),
    queryFn: () => businessProfileService.getBusinessProfiles(),
    ...options,
  });
}

// Hook to fetch specific business profile
export function useBusinessProfile(id: string, options?: BaseQueryOptions<BusinessProfile>) {
  return useQuery({
    queryKey: businessProfileKeys.detail(id),
    queryFn: () => businessProfileService.getBusinessProfile(id),
    enabled: !!id,
    ...options,
  });
}

// Hook to create business profile
export function useCreateBusinessProfile(
  options?: BaseMutationOptions<BusinessProfile, unknown, CreateBusinessProfileRequest>,
) {
  const queryClient = useQueryClient();
  const setProfile = useBusinessProfileStore((state) => state.setProfile);

  return useMutation({
    mutationFn: (data: CreateBusinessProfileRequest) => businessProfileService.createBusinessProfile(data),
    onSuccess: (newProfile) => {
      // Update store
      setProfile(newProfile);

      // Update cache
      queryClient.setQueryData(businessProfileKeys.current(), newProfile);
      queryClient.invalidateQueries({ queryKey: businessProfileKeys.list() });
    },
    ...options,
  });
}

// Hook to update business profile
export function useUpdateBusinessProfile(
  options?: BaseMutationOptions<
    BusinessProfile,
    unknown,
    { id: string; data: UpdateBusinessProfileRequest }
  >,
) {
  const queryClient = useQueryClient();
  const { profile, setProfile } = useBusinessProfileStore();

  return useMutation({
    mutationFn: ({ id, data }) => businessProfileService.updateBusinessProfile(id, data),
    onSuccess: (updatedProfile, variables) => {
      // Update store if it's the current profile
      if (profile?.id === variables.id) {
        setProfile(updatedProfile);
      }

      // Update cache
      queryClient.setQueryData(businessProfileKeys.detail(variables.id), updatedProfile);
      queryClient.setQueryData(businessProfileKeys.current(), updatedProfile);
      queryClient.invalidateQueries({ queryKey: businessProfileKeys.list() });
    },
    ...options,
  });
}

// Hook to delete business profile
export function useDeleteBusinessProfile(options?: BaseMutationOptions<void, unknown, string>) {
  const queryClient = useQueryClient();
  const { profile, clearProfile } = useBusinessProfileStore();

  return useMutation({
    mutationFn: (id: string) => businessProfileService.deleteBusinessProfile(id),
    onSuccess: (_, id) => {
      // Clear store if it's the current profile
      if (profile?.id === id) {
        clearProfile();
      }

      // Remove from cache
      queryClient.removeQueries({ queryKey: businessProfileKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: businessProfileKeys.list() });
      queryClient.invalidateQueries({ queryKey: businessProfileKeys.current() });
    },
    ...options,
  });
}

// Hook to set active profile - COMMENTED OUT: setActiveProfile method doesn't exist in service
// export function useSetActiveProfile(
//   options?: BaseMutationOptions<BusinessProfile, unknown, string>,
// ) {
//   const queryClient = useQueryClient();
//   const setProfile = useBusinessProfileStore((state) => state.setProfile);

//   return useMutation({
//     mutationFn: (id: string) => businessProfileService.setActiveProfile(id),
//     onSuccess: (profile) => {
//       // Update store
//       setProfile(profile);

//       // Update cache
//       queryClient.setQueryData(businessProfileKeys.current(), profile);
//       queryClient.invalidateQueries({ queryKey: businessProfileKeys.list() });
//     },
//     ...options,
//   });
// }

// Hook to get compliance overview
export function useBusinessProfileCompliance(id: string, options?: BaseQueryOptions<any>) {
  return useQuery({
    queryKey: businessProfileKeys.compliance(id),
    queryFn: () => businessProfileService.getBusinessProfileCompliance(id),
    enabled: !!id,
    ...options,
  });
}
