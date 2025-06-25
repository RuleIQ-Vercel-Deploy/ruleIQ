"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth-store"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Shield, BarChart, FileCheck, Users, ArrowRight } from "lucide-react"

export default function HomePage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (mounted && isAuthenticated) {
      router.push("/dashboard")
    }
  }, [mounted, isAuthenticated, router])

  const features = [
    {
      icon: Shield,
      title: "Compliance Automation",
      description: "Automate your compliance workflows with AI-powered evidence collection and gap analysis."
    },
    {
      icon: BarChart,
      title: "Real-time Monitoring",
      description: "Track your compliance posture in real-time with comprehensive dashboards and alerts."
    },
    {
      icon: FileCheck,
      title: "Policy Management",
      description: "Generate, review, and maintain compliance policies with AI assistance."
    },
    {
      icon: Users,
      title: "Team Collaboration",
      description: "Enable seamless collaboration across teams with role-based access controls."
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <div className="flex items-center justify-center mb-8">
            <Shield className="h-16 w-16 text-blue-600 mr-4" />
            <h1 className="text-5xl font-bold text-gray-900 dark:text-white">
              NexCompli
            </h1>
          </div>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
            Streamline your compliance management with AI-powered automation. 
            From gap analysis to evidence collection, manage all your compliance needs in one platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => router.push("/login")}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => router.push("/register")}
            >
              Create Account
            </Button>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-center mb-4">
                    <Icon className="h-12 w-12 text-blue-600" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* CTA Section */}
        <Card className="bg-blue-600 text-white border-0">
          <CardContent className="text-center py-12">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Transform Your Compliance Management?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of organizations already using NexCompli to streamline their compliance workflows.
            </p>
            <Button
              size="lg"
              variant="secondary"
              onClick={() => router.push("/login")}
              className="bg-white text-blue-600 hover:bg-gray-100"
            >
              Start Your Journey
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}