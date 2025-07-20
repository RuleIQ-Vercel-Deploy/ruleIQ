import { type NextRequest } from 'next/server';

/**
 * Simple in-memory rate limiting for Next.js middleware
 * In production, consider using Redis or similar persistent store
 */

interface RateLimitEntry {
  count: number;
  resetTime: number;
}

// In-memory store (will be reset on server restart)
const rateLimitStore = new Map<string, RateLimitEntry>();

// Cleanup interval to remove expired entries
setInterval(() => {
  const now = Date.now();
  for (const [key, entry] of rateLimitStore.entries()) {
    if (entry.resetTime < now) {
      rateLimitStore.delete(key);
    }
  }
}, 60000); // Clean up every minute

export interface RateLimitOptions {
  windowMs: number; // Time window in milliseconds
  maxRequests: number; // Maximum requests per window
  keyGenerator?: (request: NextRequest) => string;
  skipSuccessfulRequests?: boolean;
  skipFailedRequests?: boolean;
}

export interface RateLimitResult {
  success: boolean;
  limit: number;
  remaining: number;
  resetTime: number;
  totalHits: number;
}

/**
 * Get client IP address from request
 */
export function getClientIp(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIp = request.headers.get('x-real-ip');
  const remoteAddress = request.headers.get('remote-addr');
  
  if (forwarded) {
    // x-forwarded-for can contain multiple IPs, take the first one
    const firstIp = forwarded.split(',')[0];
    return firstIp ? firstIp.trim() : 'unknown';
  }
  
  if (realIp) {
    return realIp;
  }
  
  if (remoteAddress) {
    return remoteAddress;
  }
  
  return 'unknown';
}

/**
 * Default key generator using IP address
 */
function defaultKeyGenerator(request: NextRequest): string {
  return `rate_limit:${getClientIp(request)}`;
}

/**
 * Apply rate limiting to a request
 */
export function rateLimit(options: RateLimitOptions) {
  const {
    windowMs,
    maxRequests,
    keyGenerator = defaultKeyGenerator,
  } = options;

  return (request: NextRequest): RateLimitResult => {
    const key = keyGenerator(request);
    const now = Date.now();
    const resetTime = now + windowMs;

    // Get or create rate limit entry
    let entry = rateLimitStore.get(key);
    
    if (!entry || entry.resetTime <= now) {
      // First request or window expired, create new entry
      entry = {
        count: 1,
        resetTime,
      };
      rateLimitStore.set(key, entry);
      
      return {
        success: true,
        limit: maxRequests,
        remaining: maxRequests - 1,
        resetTime,
        totalHits: 1,
      };
    }

    // Increment counter
    entry.count++;
    
    const success = entry.count <= maxRequests;
    const remaining = Math.max(0, maxRequests - entry.count);

    return {
      success,
      limit: maxRequests,
      remaining,
      resetTime: entry.resetTime,
      totalHits: entry.count,
    };
  };
}

/**
 * Predefined rate limiters for common use cases
 */
export const rateLimiters = {
  // General API requests
  api: rateLimit({
    windowMs: 60 * 1000, // 1 minute
    maxRequests: 100,
  }),

  // Authentication endpoints
  auth: rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    maxRequests: 5, // Allow 5 login attempts per 15 minutes
    keyGenerator: (request) => `auth:${getClientIp(request)}`,
  }),

  // Password reset
  passwordReset: rateLimit({
    windowMs: 60 * 60 * 1000, // 1 hour
    maxRequests: 3, // Allow 3 password reset requests per hour
    keyGenerator: (request) => `password_reset:${getClientIp(request)}`,
  }),

  // File uploads
  upload: rateLimit({
    windowMs: 60 * 60 * 1000, // 1 hour
    maxRequests: 20, // Allow 20 file uploads per hour
    keyGenerator: (request) => `upload:${getClientIp(request)}`,
  }),

  // Contact/feedback forms
  contact: rateLimit({
    windowMs: 60 * 60 * 1000, // 1 hour
    maxRequests: 5, // Allow 5 contact form submissions per hour
    keyGenerator: (request) => `contact:${getClientIp(request)}`,
  }),
};

/**
 * Get rate limit headers for response
 */
export function getRateLimitHeaders(result: RateLimitResult): Record<string, string> {
  return {
    'X-RateLimit-Limit': result.limit.toString(),
    'X-RateLimit-Remaining': result.remaining.toString(),
    'X-RateLimit-Reset': Math.ceil(result.resetTime / 1000).toString(), // Unix timestamp
    'X-RateLimit-Used': result.totalHits.toString(),
  };
}

/**
 * Rate limiting configuration for different routes
 */
export const routeRateLimits: Record<string, (request: NextRequest) => RateLimitResult> = {
  '/api/auth/login': rateLimiters.auth,
  '/api/auth/register': rateLimiters.auth,
  '/api/auth/forgot-password': rateLimiters.passwordReset,
  '/api/auth/reset-password': rateLimiters.passwordReset,
  '/api/evidence/upload': rateLimiters.upload,
  '/api/contact': rateLimiters.contact,
};

/**
 * Apply rate limiting based on route
 */
export function applyRateLimit(request: NextRequest): RateLimitResult | null {
  const {pathname} = request.nextUrl;
  
  // Check for specific route rate limits
  const rateLimiter = routeRateLimits[pathname];
  if (rateLimiter) {
    return rateLimiter(request);
  }
  
  // Apply general API rate limiting
  if (pathname.startsWith('/api/')) {
    return rateLimiters.api(request);
  }
  
  return null;
}