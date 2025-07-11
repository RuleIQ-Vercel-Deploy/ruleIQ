import { Slack, Github, Gitlab, FileText, Bot, Folder, Users, Calendar, Layers } from "lucide-react"

// Activity type for integration logs
interface IntegrationActivity {
  id: number
  action: string
  user?: string
  timestamp: string
  status: "ok" | "error" | "info"
}

// Base integration interface
interface BaseIntegration {
  id: string
  name: string
  logo: any // LucideIcon type
  description: string
}

// Connected integration
interface ConnectedIntegration extends BaseIntegration {
  isConnected: true
  lastSync: string
  syncStatus: string
  activity: IntegrationActivity[]
}

// Disconnected integration
interface DisconnectedIntegration extends BaseIntegration {
  isConnected: false
  permissions: string[]
}

// Union type for Integration
export type Integration = ConnectedIntegration | DisconnectedIntegration

export const integrations: Integration[] = [
  {
    id: "slack",
    name: "Slack",
    logo: Slack,
    description: "Receive real-time compliance alerts and notifications in your Slack channels.",
    isConnected: true,
    lastSync: "2023-10-27T10:00:00Z",
    syncStatus: "ok",
    activity: [
      { id: 1, action: "Sync successful", timestamp: "2023-10-27T10:00:00Z", status: "ok" },
      { id: 2, action: "Configuration updated", user: "John Doe", timestamp: "2023-10-26T15:30:00Z", status: "info" },
      { id: 3, action: "Integration connected", user: "John Doe", timestamp: "2023-10-25T09:00:00Z", status: "ok" },
    ],
  },
  {
    id: "github",
    name: "GitHub",
    logo: Github,
    description: "Automatically sync code repositories and track changes for compliance evidence.",
    isConnected: true,
    lastSync: "2023-10-27T09:45:00Z",
    syncStatus: "error",
    activity: [
      { id: 1, action: "Sync failed: API token expired", timestamp: "2023-10-27T09:45:00Z", status: "error" },
      { id: 2, action: "Sync successful", timestamp: "2023-10-27T08:45:00Z", status: "ok" },
      { id: 3, action: "Integration connected", user: "Jane Smith", timestamp: "2023-10-24T11:00:00Z", status: "ok" },
    ],
  },
  {
    id: "gitlab",
    name: "GitLab",
    logo: Gitlab,
    description: "Connect your GitLab repositories to automate evidence collection from your CI/CD pipelines.",
    isConnected: false,
    permissions: ["Read user profile", "Read repository data", "Access merge requests"],
  },
  {
    id: "confluence",
    name: "Confluence",
    logo: FileText,
    description: "Link your policies and procedures directly from your Confluence knowledge base.",
    isConnected: false,
    permissions: ["Read pages and spaces", "Access user profiles"],
  },
  {
    id: "jira",
    name: "Jira",
    logo: Bot,
    description: "Create and track compliance tasks and issues directly within your Jira projects.",
    isConnected: false,
    permissions: ["Read project data", "Create and modify issues", "Access user information"],
  },
  {
    id: "aws",
    name: "Amazon Web Services",
    logo: Layers,
    description: "Monitor your AWS infrastructure and automatically collect compliance evidence.",
    isConnected: false,
    permissions: ["Read CloudTrail logs", "Access S3 buckets", "Read IAM policies", "Access compliance reports"],
  },
  {
    id: "gsuite",
    name: "Google Workspace",
    logo: Users,
    description: "Sync user management and document collaboration data for compliance tracking.",
    isConnected: false,
    permissions: ["Read user directory", "Access shared drives", "Read audit logs", "Access calendar data"],
  },
  {
    id: "office365",
    name: "Microsoft 365",
    logo: Calendar,
    description: "Connect Office 365 to track document changes and user activity.",
    isConnected: false,
    permissions: ["Read user profiles", "Access SharePoint", "Read audit logs", "Access Teams data"],
  },
  {
    id: "sharepoint",
    name: "SharePoint",
    logo: Folder,
    description: "Integrate with SharePoint to automatically sync compliance documents and policies.",
    isConnected: false,
    permissions: ["Read site collections", "Access document libraries", "Read user permissions"],
  },
]

export type ActivityLog = IntegrationActivity