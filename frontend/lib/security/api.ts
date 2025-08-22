import { type NextRequest, NextResponse } from 'next/server';
import { type ZodSchema, ZodError } from 'zod';

import { sanitizeObject } from './validation';

/**
 * Secure API utilities for ruleIQ
 */

// Rate limiting store (in production, use Redis or database)
const rateLimitStore = new Map<string, { count: number; resetTime: number }>();

export interface ApiError {
  message: string;
  code: string;
  statusCode: number;
  details?: any;
}

export class ApiSecurityError extends Error {
  constructor(
    public message: string,
    public code: string,
    public statusCode: number,
    public details?: any,
  ) {
    super(message);
    this.name = 'ApiSecurityError';
  }
}

/**
 * Rate limiting middleware
 */
export function rateLimit(options: {
  maxRequests: number;
  windowMs: number;
  keyGenerator?: (request: NextRequest) => string;
}) {
  const { maxRequests, windowMs, keyGenerator = (req) => getClientIp(req) } = options;

  return (request: NextRequest): boolean => {
    const key = keyGenerator(request);
    const now = Date.now();
    const windowStart = now - windowMs;

    // Clean up old entries
    for (const [k, v] of rateLimitStore.entries()) {
      if (v.resetTime < windowStart) {
        rateLimitStore.delete(k);
      }
    }

    const current = rateLimitStore.get(key);

    if (!current) {
      rateLimitStore.set(key, { count: 1, resetTime: now + windowMs });
      return true;
    }

    if (current.resetTime < now) {
      rateLimitStore.set(key, { count: 1, resetTime: now + windowMs });
      return true;
    }

    if (current.count >= maxRequests) {
      return false;
    }

    current.count++;
    return true;
  };
}

/**
 * Get client IP address
 */
export function getClientIp(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIp = request.headers.get('x-real-ip');

  if (forwarded) {
    const firstIp = forwarded.split(',')[0];
    return firstIp ? firstIp.trim() : 'unknown';
  }

  if (realIp) {
    return realIp;
  }

  return request.ip || 'unknown';
}

/**
 * Validate request body against Zod schema
 */
export async function validateRequestBody<T>(
  request: NextRequest,
  schema: ZodSchema<T>,
): Promise<T> {
  try {
    const contentType = request.headers.get('content-type');

    if (!contentType || !contentType.includes('application/json')) {
      throw new ApiSecurityError('Invalid content type', 'INVALID_CONTENT_TYPE', 400);
    }

    const body = await request.json();

    // Sanitize input
    const sanitizedBody = sanitizeObject(body);

    // Validate with Zod
    const validatedData = schema.parse(sanitizedBody);

    return validatedData;
  } catch {
    if (error instanceof ZodError) {
      throw new ApiSecurityError('Validation failed', 'VALIDATION_ERROR', 400, error.errors);
    }

    if (error instanceof ApiSecurityError) {
      throw error;
    }

    throw new ApiSecurityError('Invalid request body', 'INVALID_REQUEST_BODY', 400);
  }
}

/**
 * Secure API route wrapper
 */
export function createSecureApiRoute<T = any>(
  handler: (request: NextRequest, context: any) => Promise<NextResponse>,
  options: {
    methods?: string[];
    rateLimit?: {
      maxRequests: number;
      windowMs: number;
    };
    requireAuth?: boolean;
    validateBody?: ZodSchema<T>;
  } = {},
) {
  const {
    methods = ['GET'],
    rateLimit: rateLimitOptions,
    requireAuth = false,
    validateBody,
  } = options;

  return async (request: NextRequest, context: any) => {
    try {
      // Method validation
      if (!methods.includes(request.method)) {
        return NextResponse.json(
          { error: 'Method not allowed', code: 'METHOD_NOT_ALLOWED' },
          { status: 405 },
        );
      }

      // Rate limiting
      if (rateLimitOptions) {
        const rateLimiter = rateLimit(rateLimitOptions);
        if (!rateLimiter(request)) {
          return NextResponse.json(
            { error: 'Too many requests', code: 'RATE_LIMIT_EXCEEDED' },
            { status: 429 },
          );
        }
      }

      // Authentication check (placeholder - implement based on your auth system)
      if (requireAuth) {
        const authHeader = request.headers.get('authorization');
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
          return NextResponse.json(
            { error: 'Unauthorized', code: 'UNAUTHORIZED' },
            { status: 401 },
          );
        }
        // Add actual JWT validation here
      }

      // Body validation
      if (validateBody && ['POST', 'PUT', 'PATCH'].includes(request.method)) {
        await validateRequestBody(request, validateBody);
      }

      // Call the actual handler
      return await handler(request, context);
    } catch (error) {
      // TODO: Replace with proper logging

      // // TODO: Replace with proper logging

      if (error instanceof ApiSecurityError) {
        return NextResponse.json(
          {
            error: error.message,
            code: error.code,
            details: error.details,
          },
          { status: error.statusCode },
        );
      }

      // Generic error response
      return NextResponse.json(
        { error: 'Internal server error', code: 'INTERNAL_ERROR' },
        { status: 500 },
      );
    }
  };
}

/**
 * HTTPS redirect utility
 */
export function enforceHttps(request: NextRequest): NextResponse | null {
  if (
    process.env.NODE_ENV === 'production' &&
    request.headers.get('x-forwarded-proto') !== 'https'
  ) {
    const url = request.nextUrl.clone();
    url.protocol = 'https:';
    return NextResponse.redirect(url, { status: 301 });
  }
  return null;
}

/**
 * Security headers utility
 */
export function addSecurityHeaders(response: NextResponse): void {
  // Prevent XSS attacks
  response.headers.set('X-XSS-Protection', '1; mode=block');

  // Prevent MIME type sniffing
  response.headers.set('X-Content-Type-Options', 'nosniff');

  // Prevent clickjacking
  response.headers.set('X-Frame-Options', 'DENY');

  // HSTS for HTTPS enforcement
  if (process.env.NODE_ENV === 'production') {
    response.headers.set(
      'Strict-Transport-Security',
      'max-age=31536000; includeSubDomains; preload',
    );
  }

  // Referrer policy
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  // Permissions policy
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), location=(), payment=()');
}

/**
 * Content Security Policy generator
 */
export function generateCSP(
  options: {
    allowInlineStyles?: boolean;
    allowInlineScripts?: boolean;
    allowEval?: boolean;
    customSources?: {
      script?: string[];
      style?: string[];
      img?: string[];
      connect?: string[];
    };
  } = {},
): string {
  const {
    allowInlineStyles = false,
    allowInlineScripts = false,
    allowEval = false,
    customSources = {},
  } = options;

  const csp = {
    'default-src': ["'self'"],
    'script-src': [
      "'self'",
      ...(allowInlineScripts ? ["'unsafe-inline'"] : []),
      ...(allowEval ? ["'unsafe-eval'"] : []),
      ...(customSources.script || []),
    ],
    'style-src': [
      "'self'",
      ...(allowInlineStyles ? ["'unsafe-inline'"] : []),
      ...(customSources.style || []),
    ],
    'img-src': ["'self'", 'data:', 'https:', ...(customSources.img || [])],
    'connect-src': ["'self'", ...(customSources.connect || [])],
    'font-src': ["'self'", 'data:'],
    'object-src': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
    'upgrade-insecure-requests': [],
  };

  return Object.entries(csp)
    .map(([directive, sources]) => `${directive} ${sources.join(' ')}`)
    .join('; ');
}
