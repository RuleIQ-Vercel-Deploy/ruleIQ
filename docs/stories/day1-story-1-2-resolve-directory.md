# Story 1.2: Resolve Frontend Directory Structure

## Story Details
**ID**: DEPLOY-002  
**Priority**: P0 (Critical Blocker)  
**Estimated Time**: 2 hours  
**Assigned To**: DevOps Engineer  
**Day**: 1 (Sept 9)  
**Status**: Ready for Development  

## User Story
As a developer,  
I want a clean directory structure without duplication,  
so that builds are predictable and maintainable.

## Technical Context
**Current Issue**: Duplicate `frontend/frontend` folder causing build confusion  
**Impact**: Unpredictable build outputs, import resolution issues, CI/CD failures  
**Root Cause**: Likely git merge issue or misconfigured build scripts  

## Acceptance Criteria
- [ ] Eliminate duplicate `frontend/frontend` folder structure
- [ ] All build scripts reference correct paths
- [ ] Development server starts without path errors
- [ ] Production build generates output in expected location
- [ ] All imports resolve correctly after restructuring
- [ ] CI/CD pipelines execute successfully

## Implementation Steps
1. **Analyze Current Structure** (15 min)
   ```bash
   # Map out current directory structure
   tree -L 3 frontend/ > structure-before.txt
   
   # Check for duplicate files
   find frontend -type f -name "*.json" | head -20
   ```

2. **Backup Current State** (15 min)
   ```bash
   # Create backup before restructuring
   cp -r frontend frontend-backup-$(date +%Y%m%d)
   tar -czf frontend-backup-$(date +%Y%m%d).tar.gz frontend/
   ```

3. **Restructure Directories** (45 min)
   - Move files from `frontend/frontend/*` to `frontend/*`
   - Update all relative imports
   - Fix build script paths in:
     - `package.json`
     - `next.config.js`
     - `tsconfig.json`
     - `.github/workflows/*.yml`

4. **Update Configuration Files** (30 min)
   ```json
   // package.json - Update script paths
   "scripts": {
     "dev": "next dev",
     "build": "next build",
     "start": "next start"
   }
   ```

5. **Validate Changes** (15 min)
   ```bash
   # Test development server
   npm run dev
   
   # Test production build
   npm run build
   
   # Verify build output location
   ls -la .next/
   ```

## Verification Checklist
- [ ] No duplicate frontend folders exist
- [ ] `npm run dev` starts without errors
- [ ] `npm run build` completes successfully
- [ ] All imports resolve (no module not found errors)
- [ ] Hot reload works in development
- [ ] CI/CD workflows pass

## Commands
```bash
# Clean and rebuild
rm -rf node_modules .next
npm install
npm run build

# Verify no broken imports
npm run lint

# Check for duplicate directories
find . -type d -name "frontend" 2>/dev/null
```

## Definition of Done
- [ ] Directory structure cleaned and organized
- [ ] All build scripts updated and working
- [ ] No import resolution errors
- [ ] Development and production builds successful
- [ ] Changes committed with clear message
- [ ] CI/CD pipeline passes

## Rollback Plan
1. If restructuring breaks application:
   ```bash
   # Restore from backup
   rm -rf frontend
   tar -xzf frontend-backup-[date].tar.gz
   ```
2. Document specific issues encountered
3. Try alternative approach with symlinks if needed

## Notes
- Check `.gitignore` to ensure build outputs aren't committed
- Update README.md if directory structure documentation exists
- Verify Docker build context if containerized

---
**Created**: September 8, 2024  
**Last Updated**: September 8, 2024  
**Story Points**: 3