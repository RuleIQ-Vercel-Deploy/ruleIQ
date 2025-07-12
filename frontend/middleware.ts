import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { applyRateLimit, getRateLimitHeaders } from '@/lib/security/rate-limiter';

/**
 * Middleware to handle security headers and httpOnly cookie management
 */
export function middleware(request: NextRequest) {
  // Apply rate limiting
  const rateLimitResult = applyRateLimit(request);
  if (rateLimitResult) {
    if (!rateLimitResult.success) {
      // Rate limit exceeded
      const response = new NextResponse(
        JSON.stringify({
          error: 'Too many requests',
          message: 'Rate limit exceeded. Please try again later.',
          retryAfter: Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000),
        }),
        {
          status: 429,
          headers: {
            'Content-Type': 'application/json',
            ...getRateLimitHeaders(rateLimitResult),
          },
        }
      );
      return response;
    }
  }

  const response = NextResponse.next();

  // Add rate limit headers to successful responses
  if (rateLimitResult) {
    const rateLimitHeaders = getRateLimitHeaders(rateLimitResult);
    Object.entries(rateLimitHeaders).forEach(([key, value]) => {
      response.headers.set(key, value);
    });
  }

  // HTTPS enforcement in production
  if (
    process.env.NODE_ENV === 'production' &&
    request.headers.get('x-forwarded-proto') !== 'https'
  ) {
    const url = request.nextUrl.clone();
    url.protocol = 'https:';
    return NextResponse.redirect(url, { status: 301 });
  }

  // Add comprehensive security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), location=(), payment=()');
  
  // HSTS for HTTPS enforcement
  if (process.env.NODE_ENV === 'production') {
    response.headers.set(
      'Strict-Transport-Security',
      'max-age=31536000; includeSubDomains; preload'
    );
  }
  
  // Content Security Policy with enhanced security
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com", // TODO: Replace with nonces in production
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "img-src 'self' data: https: blob:",
    "font-src 'self' data: https://fonts.gstatic.com",
    "connect-src 'self' https://ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech wss: ws:",
    "media-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "upgrade-insecure-requests"
  ].join('; ');
  
  response.headers.set('Content-Security-Policy', csp);
  
  // Add security headers for API routes
  if (request.nextUrl.pathname.startsWith('/api/')) {
    response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    response.headers.set('Pragma', 'no-cache');
    response.headers.set('Expires', '0');
    response.headers.set('Surrogate-Control', 'no-store');
  }

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