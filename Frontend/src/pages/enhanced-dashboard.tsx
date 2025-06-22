import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Building2,
  FileText,
  MessageSquare,
  BarChart3,
  Plus,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
} from "lucide-react"
import { Link } from "react-router-dom"
import { BentoGrid, BentoGridItem } from "@/components/aceternity/bento-grid"
import { TextGenerateEffect } from "@/components/aceternity/text-generate-effect"

const dashboardItems = [
  {
    title: "Business Profiles",
    description: "Manage your organization profiles and compliance settings",
    header: (
      <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-blue-200 to-blue-400 dark:from-blue-900 dark:to-blue-700 flex items-center justify-center">
        <Building2 className="h-8 w-8 text-white" />
      </div>
    ),
    icon: <Building2 className="h-4 w-4 text-neutral-500" />,
    link: "/business-profiles",
    count: "3 Active",
  },
  {
    title: "Evidence Management",
    description: "Collect, organize, and manage compliance evidence",
    header: (
      <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-green-200 to-green-400 dark:from-green-900 dark:to-green-700 flex items-center justify-center">
        <FileText className="h-8 w-8 text-white" />
      </div>
    ),
    icon: <FileText className="h-4 w-4 text-neutral-500" />,
    link: "/evidence",
    count: "127 Items",
  },
  {
    title: "AI Assistant",
    description: "Get instant compliance guidance and recommendations",
    header: (
      <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-purple-200 to-purple-400 dark:from-purple-900 dark:to-purple-700 flex items-center justify-center">
        <MessageSquare className="h-8 w-8 text-white" />
      </div>
    ),
    icon: <MessageSquare className="h-4 w-4 text-neutral-500" />,
    link: "/chat",
    count: "12 Conversations",
  },
  {
    title: "Compliance Reports",
    description: "Generate comprehensive compliance and audit reports",
    header: (
      <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-orange-200 to-orange-400 dark:from-orange-900 dark:to-orange-700 flex items-center justify-center">
        <BarChart3 className="h-8 w-8 text-white" />
      </div>
    ),
    icon: <BarChart3 className="h-4 w-4 text-neutral-500" />,
    link: "/reports",
    count: "8 Generated",
  },
]

export function EnhancedDashboard() {
  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <TextGenerateEffect
          words="Welcome to your compliance command center"
          className="text-3xl font-bold text-gray-900 dark:text-white"
        />
        <p className="text-gray-600 dark:text-gray-300">
          Monitor your compliance status, manage evidence, and get AI-powered insights all in one place.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overall Compliance</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">78%</div>
            <p className="text-xs text-muted-foreground">+5% from last month</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Evidence Items</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">127</div>
            <p className="text-xs text-muted-foreground">23 added this week</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-yellow-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Actions</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">12</div>
            <p className="text-xs text-muted-foreground">3 high priority</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Interactions</CardTitle>
            <MessageSquare className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">89</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Grid */}
      <BentoGrid className="max-w-4xl mx-auto">
        {dashboardItems.map((item, i) => (
          <Link key={i} to={item.link}>
            <BentoGridItem
              title={
                <div className="flex items-center justify-between">
                  <span>{item.title}</span>
                  <span className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-full">{item.count}</span>
                </div>
              }
              description={item.description}
              header={item.header}
              icon={item.icon}
              className="hover:shadow-lg transition-shadow cursor-pointer"
            />
          </Link>
        ))}
      </BentoGrid>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Get started with common compliance tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button asChild className="h-auto p-4 flex flex-col items-start space-y-2">
              <Link to="/business-profiles/new">
                <Plus className="h-5 w-5" />
                <span className="font-medium">Create Business Profile</span>
                <span className="text-xs opacity-80">Set up a new compliance profile</span>
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-start space-y-2">
              <Link to="/evidence/new">
                <FileText className="h-5 w-5" />
                <span className="font-medium">Upload Evidence</span>
                <span className="text-xs opacity-80">Add compliance documentation</span>
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-start space-y-2">
              <Link to="/chat">
                <MessageSquare className="h-5 w-5" />
                <span className="font-medium">Ask AI Assistant</span>
                <span className="text-xs opacity-80">Get compliance guidance</span>
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Your latest compliance activities</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { action: "Evidence uploaded for GDPR Article 30", time: "2 hours ago", type: "upload" },
              { action: "Business profile updated", time: "1 day ago", type: "update" },
              { action: "Compliance assessment completed", time: "3 days ago", type: "complete" },
              { action: "AI recommendation implemented", time: "1 week ago", type: "ai" },
            ].map((activity, index) => (
              <div key={index} className="flex items-center space-x-4 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                <div
                  className={`w-2 h-2 rounded-full ${
                    activity.type === "upload"
                      ? "bg-blue-500"
                      : activity.type === "update"
                        ? "bg-green-500"
                        : activity.type === "complete"
                          ? "bg-purple-500"
                          : "bg-orange-500"
                  }`}
                />
                <div className="flex-1">
                  <p className="text-sm font-medium">{activity.action}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
