import { Plus, Download, Edit, Trash2, Eye, Settings } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function ButtonExamples() {
  return (
    <div className="space-y-6">
      {/* Dashboard Actions */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle style={{ color: "#F0EAD6" }}>Dashboard Actions</CardTitle>
          <CardDescription style={{ color: "#6C757D" }}>
            Common button combinations used in dashboard interfaces
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="primary" size="medium">
              <Plus className="h-4 w-4" />
              New Assessment
            </Button>
            <Button variant="secondary-ruleiq" size="medium">
              <Download className="h-4 w-4" />
              Export Report
            </Button>
            <Button variant="ghost-ruleiq" size="medium">
              <Settings className="h-4 w-4" />
              Settings
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Table Actions */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle style={{ color: "#F0EAD6" }}>Table Row Actions</CardTitle>
          <CardDescription style={{ color: "#6C757D" }}>Action buttons typically used in data tables</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="ghost-ruleiq" size="small">
              <Eye className="h-3 w-3" />
              View
            </Button>
            <Button variant="ghost-ruleiq" size="small">
              <Edit className="h-3 w-3" />
              Edit
            </Button>
            <Button variant="error" size="small">
              <Trash2 className="h-3 w-3" />
              Delete
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Form Actions */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle style={{ color: "#F0EAD6" }}>Form Actions</CardTitle>
          <CardDescription style={{ color: "#6C757D" }}>
            Button combinations for form submissions and actions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="primary" size="large">
              Save Changes
            </Button>
            <Button variant="secondary-ruleiq" size="large">
              Cancel
            </Button>
            <Button variant="ghost-ruleiq" size="large">
              Reset Form
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Status Actions */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle style={{ color: "#F0EAD6" }}>Status Actions</CardTitle>
          <CardDescription style={{ color: "#6C757D" }}>Buttons for different status-based actions</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="success" size="medium">
              Approve Assessment
            </Button>
            <Button variant="warning" size="medium">
              Mark for Review
            </Button>
            <Button variant="error" size="medium">
              Reject Submission
            </Button>
            <Button variant="accent" size="medium">
              Feature Request
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
