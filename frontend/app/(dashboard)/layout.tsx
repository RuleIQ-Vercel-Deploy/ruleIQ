import { stackServerApp } from "@/app/stack";
import { redirect } from "next/navigation";
import React from 'react';
import { CommandPalette } from '@/components/dashboard/command-palette';
import { KeyboardShortcutsDialog } from '@/components/dashboard/keyboard-shortcuts-dialog';
import { QuickActionsPanel } from '@/components/dashboard/quick-actions';
import { AppSidebar } from '@/components/navigation/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await stackServerApp.getUser();
  
  if (!user) {
    redirect('/login');
  }

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        {children}
        <QuickActionsPanel />
        <KeyboardShortcutsDialog />
        <CommandPalette />
      </SidebarInset>
    </SidebarProvider>
  );
}
