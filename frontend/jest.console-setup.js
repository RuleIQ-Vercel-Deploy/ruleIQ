// Capture React warnings and errors during tests
const originalError = console.error
const originalWarn = console.warn

// Track React key warnings and other critical issues
const reactKeyWarnings = []
const reactErrors = []

console.error = (...args) => {
  const message = args.join(' ')
  
  // Catch React key warnings
  if (message.includes('Warning: Encountered two children with the same key')) {
    reactKeyWarnings.push(message)
    // Fail the test immediately for duplicate keys
    throw new Error(`DUPLICATE KEY ERROR: ${message}`)
  }
  
  // Catch other React warnings that should fail tests
  if (message.includes('Warning: Each child in a list should have a unique "key" prop')) {
    reactErrors.push(message)
    throw new Error(`MISSING KEY ERROR: ${message}`)
  }
  
  if (message.includes('Warning: Failed prop type')) {
    reactErrors.push(message)
    throw new Error(`PROP TYPE ERROR: ${message}`)
  }
  
  if (message.includes('Warning: React.createElement: type is invalid')) {
    reactErrors.push(message)
    throw new Error(`INVALID ELEMENT ERROR: ${message}`)
  }
  
  // Allow other console.error calls to pass through
  originalError.apply(console, args)
}

console.warn = (...args) => {
  const message = args.join(' ')
  
  // Catch React warnings that should be treated as errors in tests
  if (message.includes('Warning: componentWillReceiveProps has been renamed')) {
    throw new Error(`DEPRECATED LIFECYCLE ERROR: ${message}`)
  }
  
  if (message.includes('Warning: componentWillMount has been renamed')) {
    throw new Error(`DEPRECATED LIFECYCLE ERROR: ${message}`)
  }
  
  // Allow other warnings to pass through
  originalWarn.apply(console, args)
}

// Global test helpers
global.getReactKeyWarnings = () => reactKeyWarnings
global.getReactErrors = () => reactErrors
global.clearReactWarnings = () => {
  reactKeyWarnings.length = 0
  reactErrors.length = 0
}
