import apiClient from "@/lib/api-client"
import type { LoginFormData, RegisterFormData } from "@/lib/validators"
import type { TokenResponse, User } from "@/lib/types/api"

export const authApi = {
  login: async (credentials: LoginFormData): Promise<{ tokens: TokenResponse; user: User }> => {
    // Use the login method from our API client
    const tokens = await apiClient.login(credentials.email, credentials.password)

    // Get user profile
    const user = await apiClient.getUserProfile()

    return {
      tokens,
      user,
    }
  },

  register: async (userData: RegisterFormData): Promise<{ tokens: TokenResponse; user: User }> => {
    // Use the register method from our API client
    await apiClient.register(userData.email, userData.password)

    // Auto-login after registration
    return authApi.login({
      email: userData.email,
      password: userData.password,
    })
  },

  logout: async (): Promise<void> => {
    await apiClient.logout()
  },

  getProfile: async (): Promise<User> => {
    return await apiClient.getUserProfile()
  },
}