import winston from 'winston';
import 'winston-daily-rotate-file';

const { combine, timestamp, printf, colorize, json } = winston.format;

const logDir = 'logs';

// Custom log format
const logFormat = printf(({ level, message, timestamp, stack }) => {
  return `${timestamp} ${level}: ${stack || message}`;
});

const logger = winston.createLogger({
  level: process.env['LOG_LEVEL'] || 'info',
  format: combine(timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }), json(), logFormat),
  transports: [
    // Console transport
    new winston.transports.Console({
      format: combine(
        colorize(),
        printf(({ level, message }) => `${level}: ${message}`),
      ),
    }),
    // File transport for all logs
    new winston.transports.DailyRotateFile({
      level: 'info',
      dirname: logDir,
      filename: '%DATE%-combined.log',
      datePattern: 'YYYY-MM-DD',
      zippedArchive: true,
      maxSize: '20m',
      maxFiles: '14d',
    }),
    // File transport for error logs
    new winston.transports.DailyRotateFile({
      level: 'error',
      dirname: logDir,
      filename: '%DATE%-error.log',
      datePattern: 'YYYY-MM-DD',
      zippedArchive: true,
      maxSize: '20m',
      maxFiles: '30d',
    }),
  ],
  exceptionHandlers: [
    new winston.transports.DailyRotateFile({
      dirname: logDir,
      filename: '%DATE%-exceptions.log',
      datePattern: 'YYYY-MM-DD',
      zippedArchive: true,
      maxSize: '20m',
      maxFiles: '30d',
    }),
  ],
  rejectionHandlers: [
    new winston.transports.DailyRotateFile({
      dirname: logDir,
      filename: '%DATE%-rejections.log',
      datePattern: 'YYYY-MM-DD',
      zippedArchive: true,
      maxSize: '20m',
      maxFiles: '30d',
    }),
  ],
  exitOnError: false,
});

// Sentry transport for production errors
if (process.env.NODE_ENV === 'production') {
  // In a real scenario, you would add a Sentry transport here.
  // For example:
  // const Sentry = require('@sentry/node');
  // logger.add(new winston.transports.Sentry({
  //   sentry: Sentry,
  //   level: 'error',
  // }));
}

export default logger;
