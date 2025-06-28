"use client"

import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { User, TokenResponse } from "@/lib/types/api"

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: User | null
  isAuthenticated: boolean
  permissions: string[]
  role: string | null
  login: (tokens: TokenResponse, user: User) => void
  logout: () => void
  setUser: (user: User) => void
  updatePermissions: (permissions: string[]) => void
  hasPermission: (permission: string) => boolean
  hasRole: (role: string) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
  hasAllPermissions: (permissions: string[]) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      permissions: [],
      role: null,

      login: (tokens, user) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem("access_token", tokens.access_token)
          localStorage.setItem("refresh_token", tokens.refresh_token)
        }
        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          user,
          isAuthenticated: true,
          permissions: user.permissions || [],
          role: user.role || null,
        })
      },

      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem("access_token")
          localStorage.removeItem("refresh_token")
        }
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
          permissions: [],
          role: null,
        })
      },

      setUser: (user) =>
        set({
          user,
          permissions: user.permissions || [],
          role: user.role || null,
        }),

      updatePermissions: (permissions) => set({ permissions }),

      hasPermission: (permission) => {
        const { permissions } = get()
        return permissions.includes(permission)
      },

      hasRole: (role) => {
        const { role: userRole } = get()
        return userRole === role
      },

      hasAnyPermission: (permissions) => {
        const { permissions: userPermissions } = get()
        return permissions.some((permission) => userPermissions.includes(permission))
      },

      hasAllPermissions: (permissions) => {
        const { permissions: userPermissions } = get()
        return permissions.every((permission) => userPermissions.includes(permission))
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        permissions: state.permissions,
        role: state.role,
      }),
      skipHydration: true,
    },
  ),
)