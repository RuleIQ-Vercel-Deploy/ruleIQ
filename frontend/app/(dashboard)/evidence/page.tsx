"use client"

import {
  Search,
  Upload,
  FileText,
  MoreVertical,
  Download,
  Trash2,
  Eye,
  // Filter,
  Shield,
  CheckCircle,
  Clock,
  XCircle
} from "lucide-react"
import { useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
// import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { evidenceData, statuses, frameworks } from "@/lib/data/evidence"
import { cn } from "@/lib/utils"

export default function EvidencePage() {
  const [selectedEvidence, setSelectedEvidence] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [frameworkFilter, setFrameworkFilter] = useState("all")

  const handleSelectionChange = (evidenceId: string) => {
    setSelectedEvidence(prev =>
      prev.includes(evidenceId)
        ? prev.filter(id => id !== evidenceId)
        : [...prev, evidenceId]
    )
  }

  const filteredEvidence = evidenceData.filter(evidence => {
    const matchesSearch = evidence.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === "all" || evidence.status === statusFilter
    const matchesFramework = frameworkFilter === "all" || evidence.frameworks.includes(frameworkFilter)
    return matchesSearch && matchesStatus && matchesFramework
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "approved":
        return <CheckCircle className="h-4 w-4" />
      case "pending":
        return <Clock className="h-4 w-4" />
      case "rejected":
        return <XCircle className="h-4 w-4" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "approved":
        return "text-success border-success/20 bg-success/10"
      case "pending":
        return "text-warning border-warning/20 bg-warning/10"
      case "rejected":
        return "text-error border-error/20 bg-error/10"
      default:
        return ""
    }
  }

  return (
    <div className="flex-1 space-y-8 p-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-navy">Evidence Library</h2>
          <p className="text-muted-foreground">
            Manage and organize your compliance documentation
          </p>
        </div>
        <Button className="bg-gold hover:bg-gold-dark text-navy">
          <Upload className="mr-2 h-4 w-4" />
          Upload Evidence
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Evidence</CardTitle>
            <FileText className="h-4 w-4 text-gold" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{evidenceData.length}</div>
            <p className="text-xs text-muted-foreground">
              +2 from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approved</CardTitle>
            <CheckCircle className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {evidenceData.filter(e => e.status === "approved").length}
            </div>
            <p className="text-xs text-muted-foreground">
              Ready for audit
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Review</CardTitle>
            <Clock className="h-4 w-4 text-warning" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {evidenceData.filter(e => e.status === "pending").length}
            </div>
            <p className="text-xs text-muted-foreground">
              Awaiting approval
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Coverage</CardTitle>
            <Shield className="h-4 w-4 text-gold" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">85%</div>
            <p className="text-xs text-muted-foreground">
              Across all frameworks
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-1 items-center gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search evidence..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              {statuses.map(status => (
                <SelectItem key={status.value} value={status.value}>
                  {status.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={frameworkFilter} onValueChange={setFrameworkFilter}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Framework" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Frameworks</SelectItem>
              {frameworks.map(framework => (
                <SelectItem key={framework.value} value={framework.value}>
                  {framework.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        {selectedEvidence.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {selectedEvidence.length} selected
            </span>
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Download
            </Button>
            <Button variant="outline" size="sm" className="text-error hover:text-error">
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          </div>
        )}
      </div>

      {/* Evidence Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredEvidence.map((evidence) => (
          <Card 
            key={evidence.id} 
            className={cn(
              "hover:shadow-lg transition-all duration-200",
              selectedEvidence.includes(evidence.id) && "ring-2 ring-gold"
            )}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <Checkbox
                    checked={selectedEvidence.includes(evidence.id)}
                    onCheckedChange={() => handleSelectionChange(evidence.id)}
                    aria-label={`Select ${evidence.name}`}
                  />
                  <FileText className="h-5 w-5 text-gold" />
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <MoreVertical className="h-4 w-4" />
                      <span className="sr-only">More actions</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuLabel>Actions</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>
                      <Eye className="mr-2 h-4 w-4" />
                      View
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-error">
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
              <CardTitle className="text-base font-semibold text-navy mt-2">
                {evidence.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Status Badge */}
              <div className="flex items-center gap-2">
                <Badge 
                  variant="outline" 
                  className={cn("gap-1", getStatusColor(evidence.status))}
                >
                  {getStatusIcon(evidence.status)}
                  {statuses.find(s => s.value === evidence.status)?.label}
                </Badge>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-1">
                {evidence.classification.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>

              {/* Frameworks */}
              <div className="flex flex-wrap gap-1">
                {evidence.frameworks.map((fw) => (
                  <Badge 
                    key={fw} 
                    variant="outline" 
                    className="text-xs border-gold/20 text-gold"
                  >
                    {frameworks.find(f => f.value === fw)?.label}
                  </Badge>
                ))}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between pt-2 text-sm text-muted-foreground">
                <span>{evidence.uploadDate}</span>
                <div className="flex items-center gap-1">
                  <div className="h-6 w-6 rounded-full bg-gold/20" />
                  <span>{evidence.uploadedBy}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredEvidence.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No evidence found</h3>
            <p className="text-sm text-muted-foreground text-center mb-4">
              {searchQuery || statusFilter !== "all" || frameworkFilter !== "all"
                ? "Try adjusting your filters or search query"
                : "Upload your first evidence document to get started"}
            </p>
            {(!searchQuery && statusFilter === "all" && frameworkFilter === "all") && (
              <Button className="bg-gold hover:bg-gold-dark text-navy">
                <Upload className="mr-2 h-4 w-4" />
                Upload Evidence
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}