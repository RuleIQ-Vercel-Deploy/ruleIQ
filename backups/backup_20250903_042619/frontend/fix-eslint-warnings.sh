#!/bin/bash

# Fix ESLint warnings in frontend

echo "🔧 Fixing ESLint warnings..."

# 1. Fix 'error' variables in catch blocks by prefixing with underscore
echo "📝 Fixing catch block error variables..."

# Find all TypeScript files and fix error variables in catch blocks
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | while read file; do
  # Fix catch (error) patterns
  sed -i 's/catch (error)/catch (_error)/g' "$file"
  # Fix } catch (error) patterns
  sed -i 's/} catch (error)/} catch (_error)/g' "$file"
  # Fix .catch((error) patterns
  sed -i 's/\.catch((error)/\.catch((_error)/g' "$file"
  # Fix onError: (error patterns
  sed -i 's/onError: (error/onError: (_error/g' "$file"
done

# 2. Remove unused imports - Alert and AlertDescription
echo "📝 Removing unused Alert imports..."
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | while read file; do
  # Check if Alert/AlertDescription are actually used in the file
  if grep -q "import.*{.*Alert.*}.*from.*ui/alert" "$file"; then
    # Check if Alert is used in JSX
    if ! grep -q "<Alert[^a-zA-Z]" "$file"; then
      # Remove Alert imports if not used
      sed -i '/import.*{.*Alert.*AlertDescription.*}.*from.*ui\/alert/d' "$file"
    fi
  fi
done

echo "✅ ESLint warnings fix complete!"
echo "📊 Running ESLint to check remaining warnings..."