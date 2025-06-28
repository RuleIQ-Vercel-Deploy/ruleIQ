"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useAuthStore } from "@/lib/store/auth-store"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { BarChart, Users, FileText, AlertTriangle, Building2, Settings } from "lucide-react"

export default function DashboardPage() {
  const { user, isAuthenticated } = useAuthStore()
  const [readinessScore] = useState(68)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])
  
  const dashboardData = {
    gaps: 12,
    expiring: 3,
    highRisk: 5,
    totalControls: 45,
  }

  const activity = [
    { user: 'Alex G.', action: 'uploaded evidence for C-05', time: '2h ago' },
    { user: 'System', action: 'synced 52 assets from AWS', time: '5h ago' },
    { user: 'Casey J.', action: 'approved "Access Control Policy"', time: '1d ago' },
  ]

  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please log in to access the dashboard</h1>
          <Button onClick={() => window.location.href = '/login'}>
            Go to Login
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="p-4 md:p-8 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Welcome back, {user?.first_name || user?.email}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/business-profile">
              <Button variant="outline">
                <Building2 className="mr-2 h-4 w-4" />
                Business Profile
              </Button>
            </Link>
            <Button variant="outline">Export Report</Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="flex flex-col justify-center items-center text-center">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold text-gray-500">
                Readiness Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative mb-4">
                <div className="w-32 h-32 rounded-full border-8 border-gray-200 dark:border-gray-700 relative">
                  <div 
                    className="absolute inset-0 rounded-full border-8 border-blue-600 border-t-transparent"
                    style={{
                      transform: `rotate(${(readinessScore * 3.6) - 90}deg)`,
                      borderTopColor: 'transparent'
                    }}
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-3xl font-bold">{readinessScore}%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Open Gaps</CardTitle>
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-500">{dashboardData.gaps}</div>
              <p className="text-xs text-muted-foreground">Remediation required</p>
            </CardContent>
          </Card>

          <Card className="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Expiring Evidence</CardTitle>
              <FileText className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-500">{dashboardData.expiring}</div>
              <p className="text-xs text-muted-foreground">Within 30 days</p>
            </CardContent>
          </Card>

          <Card className="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High-Risk Controls</CardTitle>
              <BarChart className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.highRisk}</div>
              <p className="text-xs text-muted-foreground">Unimplemented</p>
            </CardContent>
          </Card>
        </div>

        {/* Progress Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Implementation Progress</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Access Controls</span>
                  <span>85%</span>
                </div>
                <Progress value={85} />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Data Protection</span>
                  <span>72%</span>
                </div>
                <Progress value={72} />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Incident Response</span>
                  <span>45%</span>
                </div>
                <Progress value={45} />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Risk Management</span>
                  <span>60%</span>
                </div>
                <Progress value={60} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activity.map((item, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <Users className="w-5 h-5 mr-3 mt-1 text-gray-400" />
                    <div className="flex-1">
                      <p className="text-sm">
                        <span className="font-medium">{item.user}</span>{' '}
                        <span className="text-gray-600 dark:text-gray-400">{item.action}</span>
                      </p>
                      <p className="text-xs text-gray-400">{item.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="outline" className="h-16 flex flex-col items-center justify-center">
                <FileText className="h-6 w-6 mb-2" />
                <span className="text-sm">Upload Evidence</span>
              </Button>
              <Button variant="outline" className="h-16 flex flex-col items-center justify-center">
                <BarChart className="h-6 w-6 mb-2" />
                <span className="text-sm">Run Assessment</span>
              </Button>
              <Button variant="outline" className="h-16 flex flex-col items-center justify-center">
                <Users className="h-6 w-6 mb-2" />
                <span className="text-sm">Review Policies</span>
              </Button>
              <Button variant="outline" className="h-16 flex flex-col items-center justify-center">
                <AlertTriangle className="h-6 w-6 mb-2" />
                <span className="text-sm">View Gaps</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}