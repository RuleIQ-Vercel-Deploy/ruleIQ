#!/bin/bash

# Script to fix all the API parameter undefined issues in one go

# List of files and patterns to fix
declare -A fixes=(
    ["lib/api/integrations.service.ts"]='s/{ params }/params ? { params } : {}/g'
    ["lib/api/monitoring.service.ts"]='s/{ params }/params ? { params } : {}/g'
    ["lib/api/payment.service.ts"]='s/{ params }/params ? { params } : {}/g'
    ["lib/api/policies-typed.ts"]='s/{ params }/params ? { params } : {}/g'
    ["lib/api/policies.service.ts"]='s/{ params }/params ? { params } : {}/g'
    ["lib/api/readiness.service.ts"]='s/params,/params ? { params } : {},/g'
    ["lib/api/reports.service.ts"]='s/params,/params ? { params } : {},/g'
)

echo "Fixing API parameter undefined issues..."

for file in "${!fixes[@]}"; do
    if [[ -f "$file" ]]; then
        echo "Fixing $file"
        sed -i "${fixes[$file]}" "$file"
    else
        echo "Warning: $file not found"
    fi
done

echo "Done fixing API parameter issues."