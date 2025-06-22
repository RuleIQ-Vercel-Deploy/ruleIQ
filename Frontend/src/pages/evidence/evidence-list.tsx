"use client"

import type React from "react"

import { useState, useEffect, useMemo } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { PageHeader } from "@/components/layout/page-header"
import { useToast } from "@/hooks/use-toast"
import { VirtualizedList } from "@/components/ui/virtualized-list"
import { useOptimizedState } from "@/hooks/use-optimized-state"
import { usePerformance } from "@/hooks/use-performance"
import {
  FileText,
  Search,
  MoreHorizontal,
  Edit,
  Trash2,
  Download,
  Eye,
  Upload,
  Grid3X3,
  List,
  CheckCircle,
  Clock,
  XCircle,
  AlertTriangle,
  Plus,
} from "lucide-react"
import { format } from "date-fns"
import { memo, useCallback } from "react"

// Mock evidence data - in real app this would come from API
const generateMockEvidence = (count: number) => {
  return Array.from({ length: count }, (_, i) => ({
    id: `${i + 1}`,
    title: `Evidence Item ${i + 1}`,
    description: `Description for evidence item ${i + 1}`,
    framework: ["GDPR", "ISO 27001", "SOC 2", "HIPAA"][i % 4],
    control_id: `CTRL-${String(i + 1).padStart(3, "0")}`,
    evidence_type: ["Policy Document", "Training Record", "Technical Control", "Audit Report"][i % 4],
    status: ["approved", "pending", "review", "rejected"][i % 4],
    quality_score: Math.floor(Math.random() * 40) + 60,
    tags: [`tag-${i % 5}`, `category-${i % 3}`],
    created_at: new Date(Date.now() - Math.random() * 10000000000).toISOString(),
    updated_at: new Date(Date.now() - Math.random() * 1000000000).toISOString(),
    file_name: `evidence-${i + 1}.pdf`,
    file_size: `${(Math.random() * 5 + 0.5).toFixed(1)} MB`,
    uploaded_by: ["John Doe", "Jane Smith", "Mike Johnson", "Sarah Wilson"][i % 4],
  }))
}

const STATUS_COLORS = {
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
  review: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
}

const STATUS_ICONS = {
  approved: CheckCircle,
  pending: Clock,
  review: AlertTriangle,
  rejected: XCircle,
}

// Memoized evidence item component for better performance
const EvidenceItem = memo(
  ({
    item,
    isSelected,
    onToggleSelect,
    onDelete,
  }: {
    item: any
    isSelected: boolean
    onToggleSelect: (id: string) => void
    onDelete: (id: string) => void
  }) => {
    const StatusIcon = STATUS_ICONS[item.status as keyof typeof STATUS_ICONS]

    const handleToggleSelect = useCallback(() => {
      onToggleSelect(item.id)
    }, [item.id, onToggleSelect])

    const handleDelete = useCallback(() => {
      onDelete(item.id)
    }, [item.id, onDelete])

    return (
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="pt-6">
          <div className="flex items-center space-x-4">
            <Checkbox checked={isSelected} onCheckedChange={handleToggleSelect} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4 text-gray-400 flex-shrink-0" />
                <Link
                  to={`/app/evidence/${item.id}`}
                  className="font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 truncate"
                >
                  {item.title}
                </Link>
              </div>
              <p className="text-sm text-gray-500 mt-1 truncate">{item.description}</p>
              <div className="flex items-center space-x-2 mt-2">
                {item.tags.slice(0, 3).map((tag: string) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {item.tags.length > 3 && (
                  <Badge variant="secondary" className="text-xs">
                    +{item.tags.length - 3}
                  </Badge>
                )}
              </div>
            </div>
            <div className="w-24">
              <Badge variant="outline">{item.framework}</Badge>
            </div>
            <div className="w-24">
              <Badge className={STATUS_COLORS[item.status as keyof typeof STATUS_COLORS]}>
                <StatusIcon className="h-3 w-3 mr-1" />
                {item.status}
              </Badge>
            </div>
            <div className="w-24 text-center">
              <span className="text-sm font-medium">{item.quality_score}%</span>
            </div>
            <div className="w-32 text-sm text-gray-500">{format(new Date(item.updated_at), "MMM d, yyyy")}</div>
            <div className="w-16">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>Actions</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to={`/app/evidence/${item.id}`}>
                      <Eye className="h-4 w-4 mr-2" />
                      View Details
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to={`/app/evidence/${item.id}/edit`}>
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleDelete} className="text-red-600 dark:text-red-400">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  },
)

EvidenceItem.displayName = "EvidenceItem"

export function EvidenceList() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [evidence, setEvidence] = useOptimizedState(generateMockEvidence(10000)) // Large dataset for testing
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useOptimizedState(searchParams.get("search") || "")
  const [selectedFramework, setSelectedFramework] = useOptimizedState(searchParams.get("framework") || "")
  const [selectedStatus, setSelectedStatus] = useOptimizedState(searchParams.get("status") || "")
  const [selectedType, setSelectedType] = useOptimizedState(searchParams.get("type") || "")
  const [viewMode, setViewMode] = useState<"list" | "grid">((searchParams.get("view") as "list" | "grid") || "list")
  const [selectedItems, setSelectedItems] = useOptimizedState<string[]>([])
  const [deleteItems, setDeleteItems] = useState<string[]>([])
  const { toast } = useToast()
  const { measurePerformance } = usePerformance()

  useEffect(() => {
    loadEvidence()
  }, [])

  useEffect(() => {
    // Update URL params when filters change
    const params = new URLSearchParams()
    if (searchQuery) params.set("search", searchQuery)
    if (selectedFramework) params.set("framework", selectedFramework)
    if (selectedStatus) params.set("status", selectedStatus)
    if (selectedType) params.set("type", selectedType)
    if (viewMode !== "list") params.set("view", viewMode)
    setSearchParams(params)
  }, [searchQuery, selectedFramework, selectedStatus, selectedType, viewMode, setSearchParams])

  const loadEvidence = async () => {
    const loadTime = measurePerformance("evidence-load", async () => {
      try {
        setLoading(true)
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000))
        // Evidence is already set with mock data
      } catch (error) {
        console.error("Failed to load evidence:", error)
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to load evidence. Please try again.",
        })
      } finally {
        setLoading(false)
      }
    })

    console.log(`Evidence loaded in ${loadTime}ms`)
  }

  const handleBulkDelete = useCallback(async () => {
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500))
      setEvidence(evidence.filter((item) => !deleteItems.includes(item.id)))
      setSelectedItems([])
      toast({
        title: "Evidence Deleted",
        description: `${deleteItems.length} evidence items have been deleted.`,
      })
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to delete evidence items.",
      })
    } finally {
      setDeleteItems([])
    }
  }, [evidence, deleteItems, setEvidence, setSelectedItems, toast])

  const handleBulkApprove = useCallback(async () => {
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 500))
      setEvidence(evidence.map((item) => (selectedItems.includes(item.id) ? { ...item, status: "approved" } : item)))
      setSelectedItems([])
      toast({
        title: "Evidence Approved",
        description: `${selectedItems.length} evidence items have been approved.`,
      })
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to approve evidence items.",
      })
    }
  }, [evidence, selectedItems, setEvidence, setSelectedItems, toast])

  // Memoized filtered evidence for performance
  const filteredEvidence = useMemo(() => {
    return evidence.filter((item) => {
      const matchesSearch =
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.tags.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      const matchesFramework = !selectedFramework || item.framework === selectedFramework
      const matchesStatus = !selectedStatus || item.status === selectedStatus
      const matchesType = !selectedType || item.evidence_type === selectedType

      return matchesSearch && matchesFramework && matchesStatus && matchesType
    })
  }, [evidence, searchQuery, selectedFramework, selectedStatus, selectedType])

  const frameworks = useMemo(() => Array.from(new Set(evidence.map((item) => item.framework))), [evidence])
  const statuses = useMemo(() => ["approved", "pending", "review", "rejected"], [])
  const types = useMemo(() => Array.from(new Set(evidence.map((item) => item.evidence_type))), [evidence])

  const toggleSelectAll = useCallback(() => {
    if (selectedItems.length === filteredEvidence.length) {
      setSelectedItems([])
    } else {
      setSelectedItems(filteredEvidence.map((item) => item.id))
    }
  }, [selectedItems.length, filteredEvidence, setSelectedItems])

  const toggleSelectItem = useCallback(
    (id: string) => {
      setSelectedItems((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]))
    },
    [setSelectedItems],
  )

  const handleDeleteItem = useCallback((id: string) => {
    setDeleteItems([id])
  }, [])

  // Render function for virtualized list
  const renderEvidenceItem = useCallback(
    ({ index, style }: { index: number; style: React.CSSProperties }) => {
      const item = filteredEvidence[index]
      return (
        <div style={style}>
          <EvidenceItem
            item={item}
            isSelected={selectedItems.includes(item.id)}
            onToggleSelect={toggleSelectItem}
            onDelete={handleDeleteItem}
          />
        </div>
      )
    },
    [filteredEvidence, selectedItems, toggleSelectItem, handleDeleteItem],
  )

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Evidence Management" description="Loading evidence..." />
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Evidence Management"
        description={`Manage compliance evidence, documentation, and supporting materials (${filteredEvidence.length.toLocaleString()} items)`}
        breadcrumbs={[{ label: "Evidence Management" }]}
        actions={
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button asChild>
              <Link to="/app/evidence/upload">
                <Upload className="h-4 w-4 mr-2" />
                Upload Evidence
              </Link>
            </Button>
          </div>
        }
      />

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search evidence..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <select
                value={selectedFramework}
                onChange={(e) => setSelectedFramework(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Frameworks</option>
                {frameworks.map((framework) => (
                  <option key={framework} value={framework}>
                    {framework}
                  </option>
                ))}
              </select>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                {statuses.map((status) => (
                  <option key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </option>
                ))}
              </select>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                {types.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
              <div className="flex border border-gray-300 rounded-md">
                <Button
                  variant={viewMode === "list" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("list")}
                  className="rounded-r-none"
                >
                  <List className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === "grid" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("grid")}
                  className="rounded-l-none"
                >
                  <Grid3X3 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedItems.length > 0 && (
        <Card className="border-blue-200 bg-blue-50 dark:bg-blue-950 dark:border-blue-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">
                {selectedItems.length} item{selectedItems.length > 1 ? "s" : ""} selected
              </span>
              <div className="flex items-center space-x-2">
                <Button size="sm" onClick={handleBulkApprove}>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Approve
                </Button>
                <Button size="sm" variant="outline" onClick={() => setDeleteItems(selectedItems)}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
                <Button size="sm" variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Evidence List with Virtualization */}
      {filteredEvidence.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No evidence found</h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                {searchQuery || selectedFramework || selectedStatus || selectedType
                  ? "No evidence matches your current filters."
                  : "Get started by uploading your first evidence item."}
              </p>
              {!searchQuery && !selectedFramework && !selectedStatus && !selectedType && (
                <Button asChild>
                  <Link to="/app/evidence/upload">
                    <Plus className="h-4 w-4 mr-2" />
                    Upload Evidence
                  </Link>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* List Header */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-4 text-sm font-medium text-gray-500">
                <Checkbox
                  checked={selectedItems.length === filteredEvidence.length}
                  onCheckedChange={toggleSelectAll}
                />
                <div className="flex-1">Title</div>
                <div className="w-24">Framework</div>
                <div className="w-24">Status</div>
                <div className="w-24">Quality</div>
                <div className="w-32">Updated</div>
                <div className="w-16">Actions</div>
              </div>
            </CardContent>
          </Card>

          {/* Virtualized List for Performance */}
          <VirtualizedList
            height={600}
            itemCount={filteredEvidence.length}
            itemSize={120}
            renderItem={renderEvidenceItem}
            className="border rounded-md"
          />
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteItems.length > 0} onOpenChange={() => setDeleteItems([])}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Evidence</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete {deleteItems.length} evidence item{deleteItems.length > 1 ? "s" : ""}?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleBulkDelete} className="bg-red-600 hover:bg-red-700">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
