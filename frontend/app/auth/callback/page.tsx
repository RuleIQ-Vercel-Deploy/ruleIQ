'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect } from 'react';
import { Loader2 } from 'lucide-react';

import { useAppStore } from '@/lib/stores/app.store';
import { useAuthStore } from '@/lib/stores/auth.store';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { addNotification } = useAppStore();
  const { setTokens } = useAuthStore();

  useEffect(() => {
    const handleCallback = async () => {
      if (!searchParams) return;
      
      const accessToken = searchParams.get('access_token');
      const refreshToken = searchParams.get('refresh_token');
      const isNewUser = searchParams.get('new_user') === 'true';
      const error = searchParams.get('error');

      if (error) {
        addNotification({
          type: 'error',
          title: 'Authentication failed',
          message: error,
          duration: 5000,
        });
        router.push('/login');
        return;
      }

      if (accessToken && refreshToken) {
        // Set tokens in auth store
        setTokens({
          access_token: accessToken,
          refresh_token: refreshToken,
          token_type: 'bearer',
        });

        addNotification({
          type: 'success',
          title: 'Successfully signed in with Google!',
          message: isNewUser ? 'Welcome to ruleIQ!' : 'Welcome back!',
          duration: 5000,
        });

        // Redirect to appropriate page
        if (isNewUser) {
          router.push('/business-profile');
        } else {
          router.push('/dashboard');
        }
      } else {
        addNotification({
          type: 'error',
          title: 'Authentication failed',
          message: 'Invalid authentication response',
          duration: 5000,
        });
        router.push('/login');
      }
    };

    handleCallback();
  }, [searchParams, router, addNotification, setTokens]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <Loader2 className="mx-auto mb-4 h-8 w-8 animate-spin text-primary" />
        <h2 className="mb-2 text-lg font-semibold">Completing sign in...</h2>
        <p className="text-muted-foreground">Please wait while we finish logging you in.</p>
      </div>
    </div>
  );
}