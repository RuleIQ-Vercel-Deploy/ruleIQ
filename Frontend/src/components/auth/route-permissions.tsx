"use client"

// Define route permissions and roles
export const PERMISSIONS = {
  // Business Profile permissions
  BUSINESS_PROFILE_READ: "business_profile:read",
  BUSINESS_PROFILE_WRITE: "business_profile:write",
  BUSINESS_PROFILE_DELETE: "business_profile:delete",

  // Evidence permissions
  EVIDENCE_READ: "evidence:read",
  EVIDENCE_WRITE: "evidence:write",
  EVIDENCE_DELETE: "evidence:delete",
  EVIDENCE_APPROVE: "evidence:approve",

  // Assessment permissions
  ASSESSMENT_READ: "assessment:read",
  ASSESSMENT_WRITE: "assessment:write",
  ASSESSMENT_DELETE: "assessment:delete",
  ASSESSMENT_EXECUTE: "assessment:execute",

  // Report permissions
  REPORT_READ: "report:read",
  REPORT_GENERATE: "report:generate",
  REPORT_EXPORT: "report:export",

  // Team permissions
  TEAM_READ: "team:read",
  TEAM_WRITE: "team:write",
  TEAM_INVITE: "team:invite",
  TEAM_REMOVE: "team:remove",

  // Admin permissions
  ADMIN_SETTINGS: "admin:settings",
  ADMIN_USERS: "admin:users",
  ADMIN_BILLING: "admin:billing",
} as const

export const ROLES = {
  ADMIN: "admin",
  COMPLIANCE_MANAGER: "compliance_manager",
  COMPLIANCE_OFFICER: "compliance_officer",
  AUDITOR: "auditor",
  VIEWER: "viewer",
} as const

// Route permission mappings
export const ROUTE_PERMISSIONS = {
  "/app/business-profiles": [PERMISSIONS.BUSINESS_PROFILE_READ],
  "/app/business-profiles/new": [PERMISSIONS.BUSINESS_PROFILE_WRITE],
  "/app/evidence": [PERMISSIONS.EVIDENCE_READ],
  "/app/evidence/new": [PERMISSIONS.EVIDENCE_WRITE],
  "/app/assessments": [PERMISSIONS.ASSESSMENT_READ],
  "/app/assessments/new": [PERMISSIONS.ASSESSMENT_WRITE],
  "/app/reports": [PERMISSIONS.REPORT_READ],
  "/app/reports/new": [PERMISSIONS.REPORT_GENERATE],
  "/app/team": [PERMISSIONS.TEAM_READ],
  "/app/settings": [PERMISSIONS.ADMIN_SETTINGS],
} as const

// Role-based route access
export const ROLE_ROUTES = {
  [ROLES.ADMIN]: "*", // Admin can access everything
  [ROLES.COMPLIANCE_MANAGER]: [
    "/app/dashboard",
    "/app/business-profiles",
    "/app/evidence",
    "/app/assessments",
    "/app/reports",
    "/app/team",
    "/app/chat",
  ],
  [ROLES.COMPLIANCE_OFFICER]: [
    "/app/dashboard",
    "/app/business-profiles",
    "/app/evidence",
    "/app/assessments",
    "/app/reports",
    "/app/chat",
  ],
  [ROLES.AUDITOR]: ["/app/dashboard", "/app/evidence", "/app/assessments", "/app/reports", "/app/chat"],
  [ROLES.VIEWER]: ["/app/dashboard", "/app/evidence", "/app/reports", "/app/chat"],
} as const
