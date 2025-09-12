import logger from './logger';

/**
 * Creates a child logger with a specific context (e.g., component, service name).
 * This helps in filtering and analyzing logs.
 *
 * @param context - The name of the context (e.g., 'AuthService', 'UserAPI').
 * @returns A logger instance with the specified context.
 */
export const getLogger = (context: string) => {
  return logger.child({ context });
};

/**
 * Middleware for logging API requests.
 * Can be used in Next.js API routes or other server-side logic.
 */
export const withRequestLogging = (handler: Function) => async (req: any, res: any) => {
  const log = getLogger('API_Request');
  const { method, url, body, query } = req;

  log.info(`Request received: ${method} ${url}`, {
    method,
    url,
    query,
    body: body ? JSON.stringify(body, null, 2) : 'No body',
  });

  try {
    await handler(req, res);
    log.info(`Request finished: ${method} ${url}`, { status: res.statusCode });
  } catch (error: unknown) {
    log.error(`Request error: ${method} ${url}`, {
      status: 500,
      errorMessage: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
    });
    // Re-throw the error to be handled by global error handlers
    throw error;
  }
};
