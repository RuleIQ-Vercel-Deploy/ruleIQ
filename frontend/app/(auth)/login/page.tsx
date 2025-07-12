'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { Shield, Eye, EyeOff, Loader2, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import * as React from 'react';
import { useForm } from 'react-hook-form';
import * as z from 'zod';

import { SecurityBadges, TrustSignals } from '@/components/auth/security-badges';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { authService } from '@/lib/api/auth.service';
import { useAppStore } from '@/lib/stores/app.store';
import { useAuthStore } from '@/lib/stores/auth.store';
import { authSchemas } from '@/lib/security/validation';
import { useCsrfToken, getCsrfHeaders } from '@/lib/hooks/use-csrf-token';

// Use secure validation schema
type LoginFormData = z.infer<typeof authSchemas.login>;

export default function LoginPage() {
  const router = useRouter();
  const { error, clearError } = useAuthStore();
  const { addNotification } = useAppStore();
  const [showPassword, setShowPassword] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const { token: csrfToken, loading: csrfLoading, error: csrfError } = useCsrfToken();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    setError: setFormError,
  } = useForm<LoginFormData>({
    resolver: zodResolver(authSchemas.login),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  });

  const rememberMe = watch('rememberMe');

  const onSubmit = async (data: LoginFormData) => {
    if (!csrfToken) {
      setFormError('root', { message: 'Security token not available. Please refresh and try again.' });
      return;
    }

    setIsSubmitting(true);
    clearError();

    try {
      // Use auth service with CSRF protection
      await authService.login({
        email: data.email,
        password: data.password,
      }, {
        headers: getCsrfHeaders(csrfToken),
      });

      addNotification({
        type: 'success',
        title: 'Welcome back!',
        message: 'You have successfully logged in.',
        duration: 3000,
      });

      // Check if user has a business profile
      try {
        const response = await fetch('/api/business-profiles/', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });
        const profiles = await response.json();

        if (!profiles || profiles.length === 0) {
          // No business profile, redirect to setup
          router.push('/business-profile');
        } else {
          // Has profile, go to dashboard
          router.push('/dashboard');
        }
      } catch {
        // If error checking profile, go to dashboard anyway
        router.push('/dashboard');
      }
    } catch (error) {
      // Handle ApiError from the API client
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Login failed. Please check your credentials.';
      setFormError('root', { message: errorMessage });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-base">
      <div className="absolute inset-0 mesh-gradient opacity-20"></div>
      <div className="container relative mx-auto px-4 py-12">
        <div className="grid min-h-[calc(100vh-6rem)] items-center gap-16 lg:grid-cols-2">
          {/* Left side - Login Form */}
          <div className="order-1 flex items-center justify-center lg:justify-end">
            <Card className="glass-card w-full max-w-md border-0 bg-surface-primary/80 backdrop-blur-xl shadow-2xl">
              <CardHeader className="space-y-6 pb-6 text-center">
                <div className="mb-4 flex items-center justify-center gap-2">
                  <Shield className="text-brand-primary h-7 w-7" />
                  <span className="text-2xl font-bold">
                    <span className="gradient-text">ruleIQ</span>
                  </span>
                </div>
                <div>
                  <CardTitle className="mb-2 text-2xl font-bold gradient-text">Secure Login</CardTitle>
                  <CardDescription className="text-base text-text-secondary">
                    Access your AI-powered compliance dashboard
                  </CardDescription>
                </div>
                <SecurityBadges variant="compact" />
              </CardHeader>

              <CardContent className="space-y-6 px-8 pb-8">
                {/* CSRF Loading State */}
                {csrfLoading && (
                  <Alert>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <AlertDescription>Loading security verification...</AlertDescription>
                  </Alert>
                )}

                {/* CSRF Error */}
                {csrfError && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>Security verification failed: {csrfError}</AlertDescription>
                  </Alert>
                )}

                {/* Form Errors */}
                {(error || errors.root) && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error || errors.root?.message}</AlertDescription>
                  </Alert>
                )}

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  {/* Email Field */}
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-text-primary">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email"
                      {...register('email')}
                      className={errors.email ? 'border-destructive bg-surface-secondary/50' : 'bg-surface-secondary/50 border-glass-border focus:border-brand-primary'}
                      disabled={isSubmitting || csrfLoading || !!csrfError}
                    />
                    {errors.email && (
                      <p className="text-sm text-destructive">{errors.email.message}</p>
                    )}
                  </div>

                  {/* Password Field */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="password" className="text-text-primary">Password</Label>
                      <Link
                        href="/forgot-password"
                        className="text-brand-secondary hover:text-brand-secondary/80 text-sm hover:underline transition-colors"
                      >
                        Forgot password?
                      </Link>
                    </div>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Enter your password"
                        {...register('password')}
                        className={errors.password ? 'border-destructive pr-10 bg-surface-secondary/50' : 'pr-10 bg-surface-secondary/50 border-glass-border focus:border-brand-primary'}
                        disabled={isSubmitting || csrfLoading || !!csrfError}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent text-text-secondary hover:text-text-primary"
                        onClick={() => setShowPassword(!showPassword)}
                        disabled={isSubmitting || csrfLoading || !!csrfError}
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                    {errors.password && (
                      <p className="text-sm text-destructive">{errors.password.message}</p>
                    )}
                  </div>

                  {/* Remember Me */}
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="rememberMe"
                      checked={rememberMe}
                      onCheckedChange={(checked) => setValue('rememberMe', !!checked)}
                      disabled={isSubmitting || csrfLoading || !!csrfError}
                      className="border-glass-border data-[state=checked]:bg-brand-primary data-[state=checked]:border-brand-primary"
                    />
                    <Label htmlFor="rememberMe" className="cursor-pointer text-sm font-normal text-text-secondary">
                      Keep me signed in for 30 days
                    </Label>
                  </div>

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    className="btn-gradient w-full"
                    size="lg"
                    disabled={isSubmitting || csrfLoading || !!csrfError}
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Signing in...
                      </>
                    ) : (
                      'Sign In'
                    )}
                  </Button>
                </form>

                {/* OAuth Section */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-glass-border" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-surface-primary/80 px-2 text-text-tertiary">
                      Or continue with
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Button variant="outline" disabled className="bg-surface-secondary/50 border-glass-border hover:bg-surface-secondary/70 hover:border-glass-border-hover">
                    <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    Google
                  </Button>
                  <Button variant="outline" disabled className="bg-surface-secondary/50 border-glass-border hover:bg-surface-secondary/70 hover:border-glass-border-hover">
                    <svg className="mr-2 h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.554 8.623c0 .502-.045.875-.098 1.251H12.185v-2.52h6.52c-.11 1.025-.965 3.02-2.785 4.246l-.025.165 4.042 3.106.28.028C22.238 12.95 23.554 10.962 23.554 8.623M12.184 23.407c2.897 0 5.33-.952 7.106-2.589l-3.397-2.608c-.905.62-2.113 1.024-3.709 1.024-2.817 0-5.21-1.864-6.069-4.42l-.125.01-4.203 3.224-.055.152c1.754 3.456 5.363 5.207 8.452 5.207M6.116 14.814c-.229-.67-.358-1.387-.358-2.132 0-.744.13-1.462.346-2.131l-.006-.143-4.253-3.265-.139.065A11.404 11.404 0 00.63 12.682c0 1.987.378 3.889 1.076 5.474z" />
                    </svg>
                    Microsoft
                  </Button>
                </div>

                {/* Sign Up Link */}
                <div className="text-center text-sm">
                  <span className="text-text-secondary">Don&apos;t have an account? </span>
                  <Link
                    href="/register"
                    className="text-brand-secondary hover:text-brand-secondary/80 font-medium hover:underline transition-colors"
                  >
                    Create account
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right side - Trust Signals */}
          <div className="order-2 hidden lg:flex lg:items-center lg:justify-start">
            <div className="w-full max-w-lg">
              <TrustSignals />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
