/**
 * Global type definitions
 */

// Extend the Window interface if needed
declare global {
  interface Window {
    // Add any global window properties here
    Stripe?: any; // For Stripe integration
  }
}

// Re-export common types from api.ts
export type { User, AuthTokens, ApiResponse, ApiError, PaginatedResponse } from './api';

// Common types used across the application
export type Status = 'idle' | 'loading' | 'success' | 'error';

export type Priority = 'low' | 'medium' | 'high' | 'critical';

// Widget types for dashboard
export interface WidgetConfig {
  id: string;
  type: 'stats' | 'chart' | 'list' | 'activity' | 'insights';
  title: string;
  position: { x: number; y: number; w: number; h: number };
  config?: any;
  visible: boolean;
}

// Notification types
export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  read: boolean;
  created_at: string;
  action_url?: string;
}

// Theme types
export type Theme = 'light' | 'dark' | 'system';

// Make sure to export an empty object to make this a module
export {};
