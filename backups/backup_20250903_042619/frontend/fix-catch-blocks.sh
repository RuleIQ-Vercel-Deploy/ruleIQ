#!/bin/bash

echo "🔧 Fixing catch block unused errors..."

# Fix catch blocks by removing the unused error variable entirely
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | while read file; do
  # Replace catch (_error) with catch {}
  sed -i 's/catch (_error)/catch {}/g' "$file"
  sed -i 's/catch (__error)/catch {}/g' "$file"
  
  # Fix .catch((_error) => patterns
  sed -i 's/\.catch((_error) =>/\.catch(() =>/g' "$file"
  sed -i 's/\.catch((__error) =>/\.catch(() =>/g' "$file"
  
  # Fix onError: (_error) => patterns
  sed -i 's/onError: (_error) =>/onError: () =>/g' "$file"
  sed -i 's/onError: (__error) =>/onError: () =>/g' "$file"
done

echo "✅ Catch block fixes complete!"