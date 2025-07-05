// Common types to replace 'any' usage throughout the application

export type UnknownRecord = Record<string, unknown>
export type StringRecord = Record<string, string>
export type NumberRecord = Record<string, number>
export type BooleanRecord = Record<string, boolean>

// API Response types
export interface ApiResponse<T = unknown> {
  data?: T
  message?: string
  status?: number
  detail?: string
}

// Error types
export interface ApiError {
  response?: {
    data?: {
      detail?: string
      message?: string
    }
  }
  message?: string
  detail?: string
}

// Chart data types
export interface ChartDataPoint {
  name?: string
  value?: number
  date?: string
  count?: number
  week?: number
  day?: number
  [key: string]: unknown
}

// Form data types
export type FormData = Record<string, unknown>
export type FormErrors = Record<string, string | undefined>

// Event handler types
export type EventHandler<T = unknown> = (event: T) => void
export type ChangeHandler = (value: unknown) => void
export type SubmitHandler = (data: FormData) => void | Promise<void>

// Component prop types
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

// Store action types
export type StoreAction<T = void> = T extends void ? () => void : (payload: T) => void
export type AsyncStoreAction<T = void, R = void> = T extends void 
  ? () => Promise<R> 
  : (payload: T) => Promise<R>

// Utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>

// Function types
export type VoidFunction = () => void
export type AsyncVoidFunction = () => Promise<void>
export type GenericFunction<T = unknown, R = unknown> = (arg: T) => R
export type AsyncGenericFunction<T = unknown, R = unknown> = (arg: T) => Promise<R>
