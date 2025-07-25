import { z } from 'zod';

/**
 * Specify your client-side environment variables schema here.
 * This way you can ensure the app isn't built with invalid env vars.
 * To expose them to the client, prefix them with `NEXT_PUBLIC_`.
 */
const clientSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url(),
  NEXT_PUBLIC_WEBSOCKET_URL: z.string().url(),
  NEXT_PUBLIC_AUTH_DOMAIN: z.string().min(1),
  NEXT_PUBLIC_JWT_EXPIRES_IN: z.string().regex(/^\d+$/),
  NEXT_PUBLIC_ENABLE_ANALYTICS: z.string().transform((val) => val === 'true'),
  NEXT_PUBLIC_ENABLE_SENTRY: z.string().transform((val) => val === 'true'),
  NEXT_PUBLIC_ENABLE_MOCK_DATA: z.string().transform((val) => val === 'true'),
  NEXT_PUBLIC_ENV: z.enum(['development', 'production', 'test']).default('development'),
  NEXT_PUBLIC_VERCEL_ANALYTICS_ID: z.string().optional(),
});

/**
 * Specify your server-side environment variables schema here.
 * This way you can ensure the app isn't built with invalid env vars.
 */
const serverSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  SENTRY_DSN: z.string().optional(),
  SENTRY_ORG: z.string().optional(),
  SENTRY_PROJECT: z.string().optional(),
  SENTRY_AUTH_TOKEN: z.string().optional(),
});

/**
 * You can't destruct `process.env` as a regular object in the Next.js
 * middleware, so you have to do it manually here.
 */
const processEnv = {
  // Client
  NEXT_PUBLIC_API_URL: process.env['$1'],
  NEXT_PUBLIC_WEBSOCKET_URL: process.env['$1'],
  NEXT_PUBLIC_AUTH_DOMAIN: process.env['$1'],
  NEXT_PUBLIC_JWT_EXPIRES_IN: process.env['$1'],
  NEXT_PUBLIC_ENABLE_ANALYTICS: process.env['$1'],
  NEXT_PUBLIC_ENABLE_SENTRY: process.env['$1'],
  NEXT_PUBLIC_ENABLE_MOCK_DATA: process.env['$1'],
  NEXT_PUBLIC_ENV: process.env['$1'],
  NEXT_PUBLIC_VERCEL_ANALYTICS_ID: process.env['$1'],
  // Server
  NODE_ENV: process.env['$1'],
  SENTRY_DSN: process.env['$1'],
  SENTRY_ORG: process.env['$1'],
  SENTRY_PROJECT: process.env['$1'],
  SENTRY_AUTH_TOKEN: process.env['$1'],
} as const;

// Don't touch the part below
// --------------------------

const merged = serverSchema.merge(clientSchema);
// eslint-disable-next-line no-unused-vars
type _MergedInput = z.input<typeof merged>;
type MergedOutput = z.output<typeof merged>;

let env = {} as MergedOutput;
const combinedSchema = merged;

if (!!process.env['$1'] === false) {
  const isServer = typeof window === 'undefined';

  const parsed = isServer
    ? combinedSchema.safeParse(processEnv) // on server we can validate all env vars
    : clientSchema.safeParse(processEnv); // on client we can only validate the ones that are exposed

  if (parsed.success === false) {
    console.error('❌ Invalid environment variables:', parsed.error.flatten().fieldErrors);
    throw new Error('Invalid environment variables');
  }

  env = parsed.data;
} else {
  env = processEnv as MergedOutput;
}

export { env };
