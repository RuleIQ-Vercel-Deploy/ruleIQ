import { create } from 'zustand';

interface SidebarState {
  isOpen: boolean;
  isCollapsed: boolean;
}

interface ModalState {
  isOpen: boolean;
  content: React.ReactNode | null;
  title?: string;
}

interface UIState {
  // Sidebar state
  sidebar: SidebarState;
  toggleSidebar: () => void;
  setSidebarOpen: (isOpen: boolean) => void;
  toggleSidebarCollapse: () => void;
  setSidebarCollapsed: (isCollapsed: boolean) => void;

  // Modal state
  modal: ModalState;
  openModal: (content: React.ReactNode, title?: string) => void;
  closeModal: () => void;

  // Theme
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;

  // Loading states
  globalLoading: boolean;
  setGlobalLoading: (loading: boolean) => void;

  // Mobile menu
  mobileMenuOpen: boolean;
  toggleMobileMenu: () => void;
  setMobileMenuOpen: (isOpen: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  // Sidebar state
  sidebar: {
    isOpen: true,
    isCollapsed: false,
  },
  toggleSidebar: () =>
    set((state) => ({
      sidebar: { ...state.sidebar, isOpen: !state.sidebar.isOpen },
    })),
  setSidebarOpen: (isOpen) =>
    set((state) => ({
      sidebar: { ...state.sidebar, isOpen },
    })),
  toggleSidebarCollapse: () =>
    set((state) => ({
      sidebar: { ...state.sidebar, isCollapsed: !state.sidebar.isCollapsed },
    })),
  setSidebarCollapsed: (isCollapsed) =>
    set((state) => ({
      sidebar: { ...state.sidebar, isCollapsed },
    })),

  // Modal state
  modal: {
    isOpen: false,
    content: null,
    title: undefined,
  },
  openModal: (content, title) =>
    set({
      modal: {
        isOpen: true,
        content,
        title,
      },
    }),
  closeModal: () =>
    set({
      modal: {
        isOpen: false,
        content: null,
        title: undefined,
      },
    }),

  // Theme
  theme: 'light',
  setTheme: (theme) => set({ theme }),

  // Loading states
  globalLoading: false,
  setGlobalLoading: (globalLoading) => set({ globalLoading }),

  // Mobile menu
  mobileMenuOpen: false,
  toggleMobileMenu: () =>
    set((state) => ({ mobileMenuOpen: !state.mobileMenuOpen })),
  setMobileMenuOpen: (mobileMenuOpen) => set({ mobileMenuOpen }),
}));