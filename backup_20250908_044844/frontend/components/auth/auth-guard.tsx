'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores/auth.store';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  redirectTo?: string;
  fallback?: React.ReactNode;
}

export function AuthGuard({
  children,
  requireAuth = true,
  redirectTo = '/auth/login',
  fallback,
}: AuthGuardProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading, checkAuthStatus } = useAuthStore();
  const [isCheckingAuth, setIsCheckingAuth] = useState(false);

  useEffect(() => {
    // Call checkAuth on mount to verify current authentication state
    const performAuthCheck = async () => {
      setIsCheckingAuth(true);
      try {
        await checkAuthStatus();
      } finally {
        setIsCheckingAuth(false);
      }
    };

    performAuthCheck();
  }, [checkAuthStatus]);

  useEffect(() => {
    if (!isLoading && !isCheckingAuth) {
      if (requireAuth && !isAuthenticated) {
        const currentPath = window.location.pathname;
        const redirectUrl = `${redirectTo}?redirect=${encodeURIComponent(currentPath)}`;
        router.push(redirectUrl);
      } else if (!requireAuth && isAuthenticated) {
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, isLoading, isCheckingAuth, requireAuth, router, redirectTo]);

  if (isLoading || isCheckingAuth) {
    return fallback || <div data-testid="auth-loading">Loading...</div>;
  }

  if (requireAuth && !isAuthenticated) {
    return null;
  }

  if (!requireAuth && isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
