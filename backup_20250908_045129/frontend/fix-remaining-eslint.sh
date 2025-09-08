#!/bin/bash

echo "🔧 Fixing remaining ESLint warnings..."

# 1. Fix callback error parameters to use underscore prefix
echo "📝 Fixing callback error parameters..."
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | while read file; do
  # Fix .catch((error) => patterns
  sed -i 's/\.catch((\([^)]*\)error)/\.catch((\1_error)/g' "$file"
  # Fix onError: (error) => patterns  
  sed -i 's/onError: (\([^)]*\)error)/onError: (\1_error)/g' "$file"
  # Fix other callback patterns like .then((data, error) =>
  sed -i 's/, error)/, _error)/g' "$file"
done

# 2. Fix unused function parameters by prefixing with underscore
echo "📝 Fixing unused function parameters..."
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | while read file; do
  # Fix reject parameters in promises
  sed -i 's/(resolve, reject)/(resolve, _reject)/g' "$file"
  # Fix progress parameters
  sed -i 's/, progress)/, _progress)/g' "$file"
  # Fix layouts parameters
  sed -i 's/, layouts)/, _layouts)/g' "$file"
done

# 3. Comment out or remove unused imports and variables
echo "📝 Handling unused imports and variables..."

# Fix specific files with unused imports
# Dashboard layout - remove unused imports
sed -i '/import.*Loader2.*from.*lucide-react/d' ./app/\(dashboard\)/layout.tsx

# Dashboard page - remove unused import
sed -i '/import.*EnhancedStatsCard/d' ./app/\(dashboard\)/dashboard/page.tsx

# Compliance wizard - remove unused import
sed -i '/import.*useComplianceRequirements/d' ./app/\(dashboard\)/compliance-wizard/page.tsx

# Reports page - remove unused useState
sed -i 's/import { useState, useEffect }/import { useEffect }/g' ./app/\(dashboard\)/reports/page.tsx

echo "✅ Remaining ESLint warnings fix complete!"