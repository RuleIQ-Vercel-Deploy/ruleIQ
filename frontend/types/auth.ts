export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
  business_profile?: BusinessProfile
}

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  VIEWER = 'viewer'
}

export interface BusinessProfile {
  id: string
  company_name: string
  industry: string
  size: string
  compliance_frameworks?: string[]
}

export interface LoginCredentials {
  email: string
  password: string
  remember_me?: boolean
}

export interface RegisterData {
  email: string
  password: string
  full_name: string
  company_name?: string
}

export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
}

export interface TokenRefreshResponse {
  access_token: string
  refresh_token: string
  token_type: string
}