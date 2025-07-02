import { FileText, FileJson, FileImage, FileSpreadsheet } from "lucide-react"

export const statuses = [
  { value: "approved", label: "Approved", color: "bg-success" },
  { value: "pending", label: "Pending", color: "bg-warning" },
  { value: "rejected", label: "Rejected", color: "bg-error" },
] as const

export const types = [
  { value: "pdf", label: "PDF", icon: FileText },
  { value: "docx", label: "Word Document", icon: FileText },
  { value: "xlsx", label: "Spreadsheet", icon: FileSpreadsheet },
  { value: "png", label: "Image", icon: FileImage },
  { value: "json", label: "JSON", icon: FileJson },
] as const

export const frameworks = [
  { value: "gdpr", label: "GDPR" },
  { value: "iso27001", label: "ISO 27001" },
  { value: "hipaa", label: "HIPAA" },
  { value: "soc2", label: "SOC 2" },
]

export const evidenceData = [
  {
    id: "EV-001",
    name: "Q1 2024 Pen Test Results",
    status: "approved",
    type: "pdf",
    classification: ["Confidential", "Security"],
    frameworks: ["soc2", "iso27001"],
    uploadDate: "2024-06-15",
    uploadedBy: "Alice Johnson",
    userAvatar: "/placeholder.svg?height=32&width=32",
  },
  {
    id: "EV-002",
    name: "Employee Security Training Log",
    status: "approved",
    type: "xlsx",
    classification: ["Internal"],
    frameworks: ["iso27001", "gdpr"],
    uploadDate: "2024-06-12",
    uploadedBy: "Bob Williams",
    userAvatar: "/placeholder.svg?height=32&width=32",
  },
  {
    id: "EV-003",
    name: "Data Processing Agreement Template",
    status: "pending",
    type: "docx",
    classification: ["Legal", "GDPR"],
    frameworks: ["gdpr"],
    uploadDate: "2024-06-20",
    uploadedBy: "Charlie Brown",
    userAvatar: "/placeholder.svg?height=32&width=32",
  },
  {
    id: "EV-004",
    name: "Server Access Logs - May 2024",
    status: "rejected",
    type: "json",
    classification: ["Strictly Confidential", "Audit"],
    frameworks: ["soc2"],
    uploadDate: "2024-06-05",
    uploadedBy: "Diana Prince",
    userAvatar: "/placeholder.svg?height=32&width=32",
  },
  {
    id: "EV-005",
    name: "HIPAA Compliance Self-Assessment",
    status: "approved",
    type: "pdf",
    classification: ["Compliance", "Healthcare"],
    frameworks: ["hipaa"],
    uploadDate: "2024-05-28",
    uploadedBy: "Ethan Hunt",
    userAvatar: "/placeholder.svg?height=32&width=32",
  },
  {
    id: "EV-006",
    name: "Network Diagram v2.1",
    status: "pending",
    type: "png",
    classification: ["Internal", "Infrastructure"],
    frameworks: ["iso27001", "soc2"],
    uploadDate: "2024-06-22",
    uploadedBy: "Fiona Glenanne",
    userAvatar: "/placeholder.svg?height=32&width=32",
  },
]

export type Evidence = (typeof evidenceData)[0]
