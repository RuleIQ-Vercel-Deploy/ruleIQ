#!/bin/bash

# RuleIQ Application Cleanup Script
# WARNING: This will permanently remove files. Backup first!

echo "🧹 RuleIQ Application Cleanup Script"
echo "======================================"
echo ""

# Safety check
read -p "⚠️  This will clean up the application. Have you backed up important data? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled. Please backup first."
    exit 1
fi

echo "📦 Creating archive directories..."
mkdir -p archive/middleware_variants
mkdir -p archive/docker_variants
mkdir -p archive/test_results_2025
mkdir -p archive/final_backup

# 1. Middleware Consolidation
echo "🔧 Consolidating middleware files..."
if [ -f "middleware/jwt_auth.py" ]; then
    mv middleware/jwt_auth.py archive/middleware_variants/ 2>/dev/null
    mv middleware/jwt_auth_v2.py archive/middleware_variants/ 2>/dev/null
    mv middleware/jwt_auth_enhanced.py archive/middleware_variants/ 2>/dev/null
    mv middleware/jwt_decorators.py archive/middleware_variants/ 2>/dev/null
    mv middleware/cors_enhanced.py archive/middleware_variants/ 2>/dev/null
    mv middleware/rate_limiter.py archive/middleware_variants/ 2>/dev/null
    mv middleware/security_middleware_enhanced.py archive/middleware_variants/ 2>/dev/null
    echo "  ✅ Middleware consolidated"
fi

# 2. Test Results & Logs
echo "📊 Archiving test results and logs..."
mv load_test_*.csv archive/test_results_2025/ 2>/dev/null
mv load_test_*.html archive/test_results_2025/ 2>/dev/null
mv test*.xml archive/test_results_2025/ 2>/dev/null
mv *.log archive/test_results_2025/ 2>/dev/null
echo "  ✅ Test results archived"

# 3. Python Cache Cleanup
echo "🐍 Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null
rm -rf htmlcov/ 2>/dev/null
rm -f .coverage 2>/dev/null
echo "  ✅ Python caches cleaned"

# 4. Docker Compose Consolidation
echo "🐳 Consolidating Docker files..."
if [ -f "docker-compose.monitoring.yml" ]; then
    mv docker-compose.monitoring.yml archive/docker_variants/ 2>/dev/null
    mv docker-compose.neo4j.yml archive/docker_variants/ 2>/dev/null
    mv docker-compose.neon.yml archive/docker_variants/ 2>/dev/null
    mv docker-compose.freemium.yml archive/docker_variants/ 2>/dev/null
    mv docker-compose.ci.yml archive/docker_variants/ 2>/dev/null
    echo "  ✅ Docker files consolidated"
fi

# 5. Backup Management (Optional - Requires Confirmation)
echo ""
echo "⚠️  LARGE BACKUPS DETECTED (43GB):"
du -sh backup_* 2>/dev/null || echo "  No backups found"
echo ""
read -p "Do you want to remove old backups? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing old backups..."
    # Keep only the latest
    if [ -d "backup_20250908_045302" ]; then
        mv backup_20250908_045302 archive/final_backup/
    fi
    rm -rf backup_20250903_042619 2>/dev/null
    rm -rf backup_20250908_044844 2>/dev/null
    rm -rf backup_20250908_045129 2>/dev/null
    rm -rf backup_deadcode_20250908_045606 2>/dev/null
    echo "  ✅ Old backups removed"
else
    echo "  ⏭️  Skipping backup removal"
fi

# 6. Report Space Saved
echo ""
echo "📈 Cleanup Summary:"
echo "==================="

# Check if archive directory was created and has content
if [ -d "archive" ]; then
    ARCHIVE_SIZE=$(du -sh archive 2>/dev/null | cut -f1)
    echo "  📁 Archived files: $ARCHIVE_SIZE"
fi

# Estimate space saved
echo ""
echo "🎉 Cleanup Complete!"
echo ""
echo "Next Steps:"
echo "1. Review archived files in ./archive/"
echo "2. Test application functionality"
echo "3. Commit changes to git"
echo "4. Consider running: docker system prune -a"
echo ""
echo "To restore archived files:"
echo "  cp -r archive/middleware_variants/* middleware/"
echo "  cp -r archive/docker_variants/* ."