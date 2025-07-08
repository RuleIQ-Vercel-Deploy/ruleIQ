import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware to handle security headers and httpOnly cookie management
 */
export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Add security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), location=()');
  
  // Content Security Policy
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'", // Note: In production, remove unsafe-* and use nonces
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self' data:",
    "connect-src 'self' https://ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech wss:",
    "media-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "upgrade-insecure-requests"
  ].join('; ');
  
  response.headers.set('Content-Security-Policy', csp);

  // Handle refresh token cookie setting for auth endpoints
  if (request.nextUrl.pathname.startsWith('/api/auth/')) {
    // If this is a login or register response, we'll need to check for
    // refresh token in the response and set it as httpOnly cookie
    // This will be handled in the API route handlers
  }

  return response;
}

/**
 * Configure which paths this middleware runs on
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
    '/api/auth/:path*', // Run middleware on auth API routes for security headers
  ],
};