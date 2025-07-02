import { ShieldCheck, FileText, Lock, HeartHandshake, type LucideIcon } from "lucide-react"

export interface Framework {
  id: string
  name: string
  description: string
  icon: LucideIcon
}

export interface PolicyType {
  id: string
  name: string
  icon: LucideIcon
}

export const frameworks: Framework[] = [
  {
    id: "gdpr",
    name: "GDPR",
    description: "General Data Protection Regulation",
    icon: ShieldCheck,
  },
  {
    id: "iso27001",
    name: "ISO 27001",
    description: "Information Security Management",
    icon: Lock,
  },
  {
    id: "soc2",
    name: "SOC 2",
    description: "Service Organization Control 2",
    icon: FileText,
  },
  {
    id: "hipaa",
    name: "HIPAA",
    description: "Health Insurance Portability & Accountability Act",
    icon: HeartHandshake,
  },
]

export const policyTypes: PolicyType[] = [
  { id: "privacy", name: "Data Privacy", icon: ShieldCheck },
  { id: "security", name: "Information Security", icon: Lock },
  { id: "incident", name: "Incident Response", icon: FileText },
  { id: "access", name: "Access Control", icon: HeartHandshake },
  { id: "hr", name: "HR Security", icon: ShieldCheck },
  { id: "vendor", name: "Vendor Management", icon: Lock },
]

export const companyDetails = {
  name: "Innovatech Solutions Ltd.",
}

export const scopeOptions: string[] = [
  "All Employees",
  "Contractors",
  "Third-Party Vendors",
  "All Company Systems",
  "Customer Data",
  "Physical Offices",
]
