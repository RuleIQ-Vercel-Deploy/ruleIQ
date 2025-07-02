import { Slack, Github, Gitlab, FileText, Bot } from "lucide-react"

export const integrations = [
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
]

export type Integration = (typeof integrations)[0]
export type ActivityLog = (typeof integrations)[0]["activity"][0]
