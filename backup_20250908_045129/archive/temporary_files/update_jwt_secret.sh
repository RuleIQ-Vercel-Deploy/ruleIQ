#!/bin/bash
# Script to update JWT_SECRET in .env.local

echo "Updating JWT_SECRET in .env.local..."

# The new secret from the example
NEW_SECRET="nTDlGluRj39drsQ+IczE7pFw0okljEY/tKsLa+mB3d8="

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "Creating .env.local file..."
    touch .env.local
fi

# Remove any existing JWT_SECRET line
grep -v "^JWT_SECRET=" .env.local > .env.local.tmp || true

# Add the new JWT_SECRET
echo "JWT_SECRET=$NEW_SECRET" >> .env.local.tmp

# Replace the original file
mv .env.local.tmp .env.local

echo "✓ Updated .env.local with new JWT_SECRET"
echo "  JWT_SECRET=$NEW_SECRET"

# Show the result
echo ""
echo "Verifying update:"
grep "^JWT_SECRET=" .env.local

echo ""
echo "Now restart the server and run the test again:"
echo "1. pkill -f uvicorn"
echo "2. uvicorn api.main:app --reload &"
echo "3. python simple_jwt_test.py"
