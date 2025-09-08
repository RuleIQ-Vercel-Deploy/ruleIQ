#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Check if backend is running
const checkBackend = async () => {
  try {
    const response = await fetch('http://localhost:8000/openapi.json');
    if (!response.ok) {
      throw new Error(`Backend returned status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('❌ Backend is not running or OpenAPI endpoint is not accessible');
    console.error('Please start the backend with: python main.py');
    process.exit(1);
  }
};

// Generate types
const generateTypes = async () => {
  console.log('🔍 Checking backend OpenAPI endpoint...');
  const openApiSpec = await checkBackend();
  
  console.log('✅ Backend is running');
  console.log('📝 Saving OpenAPI spec...');
  
  const specPath = path.join(__dirname, '..', 'lib', 'api', 'openapi.json');
  const typesPath = path.join(__dirname, '..', 'lib', 'api', 'types.ts');
  
  // Ensure directory exists
  const apiDir = path.dirname(specPath);
  if (!fs.existsSync(apiDir)) {
    fs.mkdirSync(apiDir, { recursive: true });
  }
  
  // Save OpenAPI spec
  fs.writeFileSync(specPath, JSON.stringify(openApiSpec, null, 2));
  
  console.log('🔨 Generating TypeScript types...');
  
  // Use openapi-typescript to generate types
  const { exec } = await import('child_process');
  const { promisify } = await import('util');
  const execAsync = promisify(exec);
  
  try {
    await execAsync(`npx openapi-typescript ${specPath} -o ${typesPath}`);
    console.log('✅ Types generated successfully at lib/api/types.ts');
  } catch (error) {
    console.error('❌ Failed to generate types:', error);
    process.exit(1);
  }
};

generateTypes().catch(console.error);