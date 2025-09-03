import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface AppState {
  // Sidebar state
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;

  // Theme
  theme: 'light' | 'dark' | 'system';

  // Global loading states
  globalLoading: boolean;
  loadingMessage: string | null;

  // Notifications
  notifications: Notification[];

  // Actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  setGlobalLoading: (loading: boolean, message?: string) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  timestamp: Date;
  duration?: number; // in milliseconds, 0 means persistent
}

export const useAppStore = create<AppState>()(
  devtools(
    (set, get) => ({
      // Initial state
      sidebarOpen: true,
      sidebarCollapsed: false,
      theme: 'dark',
      globalLoading: false,
      loadingMessage: null,
      notifications: [],

      // Actions
      toggleSidebar: () =>
        set(
          (state) => ({
            sidebarOpen: !state.sidebarOpen,
          }),
          false,
          'toggleSidebar',
        ),

      setSidebarOpen: (open) => set({ sidebarOpen: open }, false, 'setSidebarOpen'),

      setSidebarCollapsed: (collapsed) =>
        set({ sidebarCollapsed: collapsed }, false, 'setSidebarCollapsed'),

      setTheme: (theme) => {
        set({ theme }, false, 'setTheme');

        // Apply theme to document
        if (
          theme === 'dark' ||
          (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
        ) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      },

      setGlobalLoading: (loading, message) =>
        set(
          {
            globalLoading: loading,
            loadingMessage: message || null,
          },
          false,
          'setGlobalLoading',
        ),

      addNotification: (notification) => {
        const id = crypto.randomUUID();
        const newNotification: Notification = {
          ...notification,
          id,
          timestamp: new Date(),
        };

        set(
          (state) => ({
            notifications: [...state.notifications, newNotification],
          }),
          false,
          'addNotification',
        );

        // Auto-remove notification after duration
        if (notification.duration && notification.duration > 0) {
          setTimeout(() => {
            get().removeNotification(id);
          }, notification.duration);
        }
      },

      removeNotification: (id) =>
        set(
          (state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          }),
          false,
          'removeNotification',
        ),

      clearNotifications: () => set({ notifications: [] }, false, 'clearNotifications'),
    }),
    {
      name: 'app-store',
    },
  ),
);

// Selectors
export const selectSidebarOpen = (state: AppState) => state.sidebarOpen;
export const selectTheme = (state: AppState) => state.theme;
export const selectNotifications = (state: AppState) => state.notifications;
export const selectGlobalLoading = (state: AppState) => state.globalLoading;
