import chalk from 'chalk';

/**
 * @typedef {object} EnvValidationResult
 * @property {boolean} isValid - Whether all required environment variables are present.
 * @property {string[]} missingVars - A list of missing environment variable names.
 */

/**
 * Validates that all required environment variables are present.
 *
 * @param {string[]} requiredVars - An array of strings, where each string is the name of a required environment variable.
 * @returns {EnvValidationResult} - An object containing the validation result.
 */
function validateEnv(requiredVars) {
  const missingVars = [];

  for (const varName of requiredVars) {
    if (!process.env[varName]) {
      missingVars.push(varName);
    }
  }

  return {
    isValid: missingVars.length === 0,
    missingVars,
  };
}

// --- Configuration ---
// Add all environment variables required for your application build and runtime here.
const REQUIRED_ENV_VARS = [
  'NODE_ENV',
  'NEXT_PUBLIC_API_URL',
  // Add other critical variables below, for example:
  // 'DATABASE_URL',
  // 'AUTH_SECRET',
];

// --- Execution ---
console.log(chalk.cyan('🔍 Validating environment variables...'));

const { isValid, missingVars } = validateEnv(REQUIRED_ENV_VARS);

if (isValid) {
  console.log(chalk.green('✅ All required environment variables are set.'));
  process.exit(0);
} else {
  console.error(chalk.red('❌ Error: Missing required environment variables:'));
  missingVars.forEach((varName) => {
    console.error(chalk.yellow(`  - ${varName}`));
  });
  console.error(
    chalk.blue(
      '\nPlease set these variables in your environment or .env file. In a CI/CD environment, ensure they are configured as secrets.',
    ),
  );
  process.exit(1);
}
