import apiClient from "@/lib/api-client"
import type { LoginInput, RegisterInput } from "@/lib/validators"
import type { TokenResponse, User } from "@/types/api"

export const authApi = {
  login: async (credentials: LoginInput): Promise<{ tokens: TokenResponse; user: User }> => {
    const formData = new FormData()
    formData.append("username", credentials.email)
    formData.append("password", credentials.password)

    const response = await apiClient.post("/auth/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    })

    // Get user profile after login
    const userResponse = await apiClient.get("/users/profile", {
      headers: {
        Authorization: `Bearer ${response.data.access_token}`,
      },
    })

    return {
      tokens: response.data,
      user: userResponse.data,
    }
  },

  register: async (userData: RegisterInput): Promise<{ tokens: TokenResponse; user: User }> => {
    const response = await apiClient.post("/auth/register", {
      email: userData.email,
      password: userData.password,
    })

    // Auto-login after registration
    return authApi.login({
      email: userData.email,
      password: userData.password,
    })
  },

  logout: async (): Promise<void> => {
    await apiClient.post("/auth/logout")
  },

  getProfile: async (): Promise<User> => {
    const response = await apiClient.get("/users/profile")
    return response.data
  },
}