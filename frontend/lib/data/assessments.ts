import { Shield, FileText, Heart, Banknote } from "lucide-react"

export const frameworks = [
  {
    value: "gdpr",
    label: "GDPR",
    icon: Shield,
  },
  {
    value: "iso 27001",
    label: "ISO 27001",
    icon: FileText,
  },
  {
    value: "hipaa",
    label: "HIPAA",
    icon: Heart,
  },
  {
    value: "fca",
    label: "FCA",
    icon: Banknote,
  },
]

export const statuses = [
  {
    value: "completed",
    label: "Completed",
    color: "bg-success/20 text-success border-success/30",
    progressColor: "success",
  },
  {
    value: "in progress",
    label: "In Progress",
    color: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    progressColor: "info",
  },
  {
    value: "overdue",
    label: "Overdue",
    color: "bg-error/20 text-error border-error/30",
    progressColor: "error",
  },
  {
    value: "scheduled",
    label: "Scheduled",
    color: "bg-grey-600/20 text-grey-300 border-grey-600/30",
    progressColor: "warning",
  },
]

export type Assessment = {
  id: string
  name: string
  framework: string
  status: "completed" | "in progress" | "overdue" | "scheduled"
  progress: number
  date: string
}

export const sampleAssessments: Assessment[] = [
  {
    id: "ASM-001",
    name: "Q1 2024 GDPR Data Protection Audit",
    framework: "gdpr",
    status: "overdue",
    progress: 75,
    date: "2024-03-15",
  },
  {
    id: "ASM-002",
    name: "Financial Reporting Compliance (Annual)",
    framework: "fca",
    status: "in progress",
    progress: 45,
    date: "2024-04-30",
  },
  {
    id: "ASM-003",
    name: "Health & Safety Workplace Review",
    framework: "iso 27001",
    status: "scheduled",
    progress: 0,
    date: "2024-05-10",
  },
  {
    id: "ASM-004",
    name: "ISO 27001 Security Assessment",
    framework: "iso 27001",
    status: "completed",
    progress: 100,
    date: "2024-02-28",
  },
  {
    id: "ASM-005",
    name: "Patient Data Privacy Check (HIPAA)",
    framework: "hipaa",
    status: "in progress",
    progress: 62,
    date: "2024-05-28",
  },
  {
    id: "ASM-006",
    name: "Employee Training Compliance Verification",
    framework: "gdpr",
    status: "completed",
    progress: 100,
    date: "2024-03-25",
  },
]
