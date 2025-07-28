'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { useAuthStore } from '@/lib/stores/auth.store';

interface AuthGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export function AuthGuard({ 
  children, 
  fallback = <div>Loading...</div>,
  redirectTo = '/auth/login' 
}: AuthGuardProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      await checkAuth();
      setIsChecking(false);
    };

    initAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isChecking && !isLoading && !isAuthenticated) {
      // Store the current path for redirect after login
      const currentPath = window.location.pathname;
      const searchParams = new URLSearchParams({
        redirect: currentPath,
      });
      
      router.push(`${redirectTo}?${searchParams.toString()}`);
    }
  }, [isAuthenticated, isLoading, isChecking, router, redirectTo]);

  // Show loading state while checking authentication
  if (isChecking || isLoading) {
    return <>{fallback}</>;
  }

  // Show nothing while redirecting unauthenticated users
  if (!isAuthenticated) {
    return null;
  }

  // Render children for authenticated users
  return <>{children}</>;
}