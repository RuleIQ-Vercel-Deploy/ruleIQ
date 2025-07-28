import React from 'react';

import { AuthGuard } from '@/components/auth/auth-guard';
import { CommandPalette } from '@/components/dashboard/command-palette';
import { KeyboardShortcutsDialog } from '@/components/dashboard/keyboard-shortcuts-dialog';
import { QuickActionsPanel } from '@/components/dashboard/quick-actions';
import { AppSidebar } from '@/components/navigation/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          {children}
          <QuickActionsPanel />
          <KeyboardShortcutsDialog />
          <CommandPalette />
        </SidebarInset>
      </SidebarProvider>
    </AuthGuard>
  );
}
