import { CheckCircle, AlertTriangle, XCircle } from "lucide-react"

export const assessmentResults = {
  id: "ASM-001",
  title: "Q1 2024 GDPR Data Protection Audit",
  overallScore: 78,
  summary:
    "The organization demonstrates a good level of compliance with GDPR, but key areas require attention, particularly in data breach procedures and third-party risk management.",
  requirements: [
    {
      id: "data-processing",
      title: "Data Processing Activities",
      score: 95,
      status: "compliant",
      icon: CheckCircle,
      color: "text-success",
    },
    {
      id: "data-subject-rights",
      title: "Data Subject Rights",
      score: 85,
      status: "compliant",
      icon: CheckCircle,
      color: "text-success",
    },
    {
      id: "security-measures",
      title: "Security Measures",
      score: 70,
      status: "partial",
      icon: AlertTriangle,
      color: "text-warning",
    },
    {
      id: "data-breaches",
      title: "Data Breaches",
      score: 40,
      status: "non-compliant",
      icon: XCircle,
      color: "text-error",
    },
    {
      id: "third-party-risk",
      title: "Third-Party Risk",
      score: 65,
      status: "partial",
      icon: AlertTriangle,
      color: "text-warning",
    },
  ],
  gapAnalysis: [
    { name: "Data Processing", score: 95 },
    { name: "Subject Rights", score: 85 },
    { name: "Security", score: 70 },
    { name: "Breaches", score: 40 },
    { name: "Third-Party Risk", score: 65 },
  ],
  recommendations: [
    {
      id: "rec-1",
      text: "Develop and document a formal data breach notification procedure, including internal escalation paths and timelines for reporting to the ICO.",
      priority: "High",
    },
    {
      id: "rec-2",
      text: "Implement a more robust due diligence process for third-party vendors, including mandatory Data Processing Agreements (DPAs) and periodic security reviews.",
      priority: "High",
    },
    {
      id: "rec-3",
      text: "Enhance data-at-rest encryption standards for non-production environments to align with production systems.",
      priority: "Medium",
    },
    {
      id: "rec-4",
      text: "Conduct regular refresher training for staff on handling Data Subject Access Requests (DSARs).",
      priority: "Low",
    },
  ],
}

export type AssessmentResultsData = typeof assessmentResults
