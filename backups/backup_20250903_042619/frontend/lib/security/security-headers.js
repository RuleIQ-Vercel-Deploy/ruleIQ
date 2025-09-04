/**
 * Security Headers Configuration
 * Comprehensive security headers for production deployment
 */

const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  {
    key: 'Permissions-Policy',
    value:
      'camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=()',
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block',
  },
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://www.googletagmanager.com https://www.google-analytics.com",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "img-src 'self' data: https: http:",
      "font-src 'self' https://fonts.gstatic.com",
      "connect-src 'self' https://api.ruleiq.com https://api-staging.ruleiq.com https://sentry.io https://www.google-analytics.com",
      "frame-src 'self' https://js.stripe.com",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join('; '),
  },
];

// API-specific security headers
const apiSecurityHeaders = [
  ...securityHeaders,
  {
    key: 'Cache-Control',
    value: 'no-cache, no-store, must-revalidate',
  },
  {
    key: 'Pragma',
    value: 'no-cache',
  },
  {
    key: 'Expires',
    value: '0',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'X-RateLimit-Limit',
    value: '100',
  },
  {
    key: 'X-RateLimit-Remaining',
    value: '99', // This would be dynamic in real implementation
  },
];

// Development vs production headers
const getSecurityHeaders = (environment = 'production') => {
  if (environment === 'development') {
    return [
      ...securityHeaders.filter((h) => h.key !== 'Content-Security-Policy'),
      {
        key: 'Content-Security-Policy',
        value:
          "default-src * 'unsafe-inline' 'unsafe-eval'; script-src * 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline';",
      },
    ];
  }

  return securityHeaders;
};

// CSP nonce generation for inline scripts
const generateCSPNonce = () => {
  return Buffer.from(crypto.randomBytes(16)).toString('base64');
};

// Security middleware for API routes
const securityMiddleware = (req, res, next) => {
  const headers = req.path.startsWith('/api') ? apiSecurityHeaders : getSecurityHeaders();

  headers.forEach((header) => {
    res.setHeader(header.key, header.value);
  });

  next();
};

// Security check utility
const checkSecurityHeaders = async (url) => {
  try {
    const response = await fetch(url, { method: 'HEAD' });
    const headers = response.headers;

    const checks = {
      'X-Frame-Options': headers.get('X-Frame-Options') === 'DENY',
      'X-Content-Type-Options': headers.get('X-Content-Type-Options') === 'nosniff',
      'Strict-Transport-Security': headers
        .get('Strict-Transport-Security')
        ?.includes('max-age=63072000'),
      'Content-Security-Policy': !!headers.get('Content-Security-Policy'),
      'Referrer-Policy': headers.get('Referrer-Policy') === 'strict-origin-when-cross-origin',
      'Permissions-Policy': !!headers.get('Permissions-Policy'),
      'X-XSS-Protection': headers.get('X-XSS-Protection') === '1; mode=block',
    };

    return {
      url,
      checks,
      score: (Object.values(checks).filter(Boolean).length / Object.keys(checks).length) * 100,
      missing: Object.keys(checks).filter((key) => !checks[key]),
    };
  } catch (error) {
    return {
      url,
      error: error.message,
      score: 0,
    };
  }
};

// Security configuration for Next.js
const securityConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: getSecurityHeaders(),
      },
      {
        source: '/api/(.*)',
        headers: apiSecurityHeaders,
      },
    ];
  },
};

module.exports = {
  securityHeaders,
  apiSecurityHeaders,
  getSecurityHeaders,
  generateCSPNonce,
  securityMiddleware,
  checkSecurityHeaders,
  securityConfig,
};
