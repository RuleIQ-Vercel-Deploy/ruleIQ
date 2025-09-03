export interface User {
  id: string;
  email: string;
  displayName?: string;
  firstName?: string;
  lastName?: string;
  companyName?: string;
  companyId?: string;
  businessProfile?: {
    id: string;
    name: string;
    industry?: string;
    size?: string;
    country?: string;
  };
  role: 'admin' | 'user' | 'owner';
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
}

export interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  confirmPassword: string;
  companyName?: string;
  firstName?: string;
  lastName?: string;
}
