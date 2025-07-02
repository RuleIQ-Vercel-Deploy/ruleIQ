"use client"

import { 
  BarChart3, 
  Download, 
  Calendar, 
  TrendingUp, 
  FileText,
  Eye,
  RefreshCw,
  Filter
} from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"


export default function ReportsPage() {
  const reports = [
    {
      name: "Monthly Compliance Report",
      type: "Compliance Overview",
      period: "January 2024",
      status: "Ready",
      description: "Comprehensive monthly compliance status report",
      lastGenerated: "2024-02-01",
      size: "2.4 MB",
    },
    {
      name: "GDPR Audit Report",
      type: "Data Protection",
      period: "Q4 2023",
      status: "Generated",
      description: "Detailed GDPR compliance audit findings",
      lastGenerated: "2024-01-15",
      size: "1.8 MB",
    },
    {
      name: "Risk Assessment Summary",
      type: "Risk Management",
      period: "2023 Annual",
      status: "Processing",
      description: "Annual risk assessment and mitigation strategies",
      lastGenerated: "2024-01-10",
      size: "3.2 MB",
    },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "Ready":
        return <Download className="h-4 w-4" />
      case "Generated":
        return <FileText className="h-4 w-4" />
      case "Processing":
        return <RefreshCw className="h-4 w-4 animate-spin" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Ready":
        return "text-success border-success/20 bg-success/10"
      case "Generated":
        return "text-info border-info/20 bg-info/10"
      case "Processing":
        return "text-warning border-warning/20 bg-warning/10"
      default:
        return ""
    }
  }

  return (
    <div className="flex-1 space-y-8 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-navy">Reports & Analytics</h2>
          <p className="text-muted-foreground">
            Generate, view, and export compliance reports
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Filter className="mr-2 h-4 w-4" />
            Filter
          </Button>
          <Button className="bg-gold hover:bg-gold-dark text-navy">
            <BarChart3 className="mr-2 h-4 w-4" />
            Generate Report
          </Button>
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {reports.map((report, index) => (
          <Card key={index} className="hover:shadow-lg transition-all duration-200">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-gold" />
                  <CardTitle className="text-lg text-navy">{report.name}</CardTitle>
                </div>
                <Badge 
                  variant="outline" 
                  className={`gap-1 ${getStatusColor(report.status)}`}
                >
                  {getStatusIcon(report.status)}
                  {report.status}
                </Badge>
              </div>
              <CardDescription className="mt-2">{report.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Metadata */}
              <div className="space-y-2 text-sm text-muted-foreground">
                <div className="flex items-center justify-between">
                  <span>Type</span>
                  <span className="font-medium text-foreground">{report.type}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Period</span>
                  <span className="font-medium text-foreground">{report.period}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Generated</span>
                  <span className="font-medium text-foreground">{report.lastGenerated}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Size</span>
                  <span className="font-medium text-foreground">{report.size}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 pt-2">
                <Button variant="outline" size="sm" className="flex-1">
                  <Eye className="mr-2 h-4 w-4" />
                  View
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex-1"
                  disabled={report.status === "Processing"}
                >
                  <Download className="mr-2 h-4 w-4" />
                  Export
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {reports.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Reports Available</h3>
            <p className="text-sm text-muted-foreground text-center mb-4 max-w-md">
              Generate your first compliance report to start tracking your organization's compliance status.
            </p>
            <Button className="bg-gold hover:bg-gold-dark text-navy">
              <BarChart3 className="mr-2 h-4 w-4" />
              Generate Your First Report
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
