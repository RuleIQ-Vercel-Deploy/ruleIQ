import * as Sentry from '@sentry/nextjs';

const SENTRY_DSN = process.env['NEXT_PUBLIC_SENTRY_DSN'];

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,

    // Adjust this value in production, or use tracesSampler for greater control
    tracesSampleRate: process.env['NODE_ENV'] === 'production' ? 0.1 : 1.0,

    // Server-side integrations
    integrations: [
      // Replaced deprecated nodeTracingIntegration with httpIntegration
      Sentry.httpIntegration(),
      Sentry.prismaIntegration(),
    ],

    // Environment configuration
    environment: process.env['NODE_ENV'],

    // Release tracking
    release: process.env['NEXT_PUBLIC_SENTRY_RELEASE'] || 'ruleiq-frontend@unknown',

    // Performance Monitoring for server
    tracesSampler: (samplingContext) => {
      const { name, attributes } = samplingContext;

      // Lower sampling for health checks
      if (name === 'GET /api/health') {
        return 0.1;
      }

      // Higher sampling for API routes in general
      if (name?.startsWith('GET /api/') || name?.startsWith('POST /api/')) {
        return process.env['NODE_ENV'] === 'production' ? 0.3 : 1.0;
      }

      // Database operations
      if (attributes?.['db.operation']) {
        return process.env['NODE_ENV'] === 'production' ? 0.1 : 0.5;
      }

      return process.env['NODE_ENV'] === 'production' ? 0.1 : 1.0;
    },

    // Error filtering for server
    beforeSend(event) {
      // Filter out known development errors
      if (process.env['NODE_ENV'] === 'development') {
        // Skip some common development noise
        if (event.exception?.values?.[0]?.value?.includes('ECONNREFUSED')) {
          return null;
        }
      }

      // Add server context
      event.tags = {
        ...event.tags,
        component: 'server',
      };

      return event;
    },

    // Server-specific configuration
    maxBreadcrumbs: 50,

    // Initial scope for server
    initialScope: {
      tags: {
        component: 'server',
        runtime: 'nodejs',
      },
    },
  });
}
