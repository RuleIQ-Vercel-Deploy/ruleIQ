"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { PageHeader } from "@/components/layout/page-header"
import { LoadingLayout } from "@/components/layout/loading-layout"
import { integrationsApi } from "@/api/integrations"
import { Search, Star, ExternalLink, Shield, Zap, Clock } from "lucide-react"
import { Link } from "react-router-dom"

export function IntegrationMarketplace() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [selectedComplexity, setSelectedComplexity] = useState<string>("all")

  const { data: providers, isLoading } = useQuery({
    queryKey: ["integration-providers"],
    queryFn: integrationsApi.getProviders,
  })

  if (isLoading) {
    return <LoadingLayout />
  }

  const categories = [
    { value: "all", label: "All Categories" },
    { value: "cloud_storage", label: "Cloud Storage" },
    { value: "identity_provider", label: "Identity Provider" },
    { value: "security_tool", label: "Security Tools" },
    { value: "monitoring", label: "Monitoring" },
    { value: "documentation", label: "Documentation" },
    { value: "ticketing", label: "Ticketing" },
    { value: "other", label: "Other" },
  ]

  const complexityLevels = [
    { value: "all", label: "All Levels" },
    { value: "easy", label: "Easy" },
    { value: "medium", label: "Medium" },
    { value: "advanced", label: "Advanced" },
  ]

  const filteredProviders =
    providers?.filter((provider) => {
      const matchesSearch =
        provider.display_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        provider.description.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesCategory = selectedCategory === "all" || provider.category === selectedCategory
      const matchesComplexity = selectedComplexity === "all" || provider.setup_complexity === selectedComplexity

      return matchesSearch && matchesCategory && matchesComplexity
    }) || []

  const popularProviders = filteredProviders.filter((p) => p.is_popular)
  const otherProviders = filteredProviders.filter((p) => !p.is_popular)

  const getComplexityIcon = (complexity: string) => {
    switch (complexity) {
      case "easy":
        return <Zap className="h-4 w-4 text-green-500" />
      case "medium":
        return <Clock className="h-4 w-4 text-yellow-500" />
      case "advanced":
        return <Shield className="h-4 w-4 text-red-500" />
      default:
        return null
    }
  }

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case "easy":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
      case "medium":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
      case "advanced":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Integration Marketplace"
        description="Discover and connect third-party integrations to enhance your compliance workflow"
      />

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search integrations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                {categories.map((category) => (
                  <SelectItem key={category.value} value={category.value}>
                    {category.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedComplexity} onValueChange={setSelectedComplexity}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Complexity" />
              </SelectTrigger>
              <SelectContent>
                {complexityLevels.map((level) => (
                  <SelectItem key={level.value} value={level.value}>
                    {level.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Popular Integrations */}
      {popularProviders.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Star className="h-5 w-5 text-yellow-500" />
            <h2 className="text-xl font-semibold">Popular Integrations</h2>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {popularProviders.map((provider) => (
              <Card key={provider.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <img
                        src={provider.logo_url || "/placeholder.svg"}
                        alt={provider.display_name}
                        className="h-12 w-12 rounded"
                      />
                      <div>
                        <CardTitle className="text-lg">{provider.display_name}</CardTitle>
                        <CardDescription>{provider.category.replace("_", " ")}</CardDescription>
                      </div>
                    </div>
                    <Badge variant="secondary">
                      <Star className="h-3 w-3 mr-1" />
                      Popular
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">{provider.description}</p>

                  <div className="flex flex-wrap gap-2">
                    <Badge className={getComplexityColor(provider.setup_complexity)}>
                      {getComplexityIcon(provider.setup_complexity)}
                      <span className="ml-1">{provider.setup_complexity}</span>
                    </Badge>
                    {provider.is_enterprise && <Badge variant="outline">Enterprise</Badge>}
                    <Badge variant="outline">{provider.auth_type.replace("_", " ")}</Badge>
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-medium text-muted-foreground">Supported Features:</p>
                    <div className="flex flex-wrap gap-1">
                      {provider.supported_features.slice(0, 3).map((feature) => (
                        <Badge key={feature} variant="secondary" className="text-xs">
                          {feature}
                        </Badge>
                      ))}
                      {provider.supported_features.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{provider.supported_features.length - 3} more
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <Button variant="outline" size="sm" asChild>
                      <a href={provider.documentation_url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Docs
                      </a>
                    </Button>
                    <Button size="sm" asChild>
                      <Link to={`/app/integrations/setup/${provider.id}`}>Connect</Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* All Integrations */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">All Integrations ({filteredProviders.length})</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {otherProviders.map((provider) => (
            <Card key={provider.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <img
                      src={provider.logo_url || "/placeholder.svg"}
                      alt={provider.display_name}
                      className="h-10 w-10 rounded"
                    />
                    <div>
                      <CardTitle className="text-base">{provider.display_name}</CardTitle>
                      <CardDescription className="text-sm">{provider.category.replace("_", " ")}</CardDescription>
                    </div>
                  </div>
                  {provider.is_enterprise && (
                    <Badge variant="outline" className="text-xs">
                      Enterprise
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground line-clamp-2">{provider.description}</p>

                <div className="flex items-center justify-between">
                  <Badge className={getComplexityColor(provider.setup_complexity)}>
                    {getComplexityIcon(provider.setup_complexity)}
                    <span className="ml-1">{provider.setup_complexity}</span>
                  </Badge>
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm" asChild>
                      <a href={provider.documentation_url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>
                    <Button size="sm" asChild>
                      <Link to={`/app/integrations/setup/${provider.id}`}>Connect</Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {filteredProviders.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No integrations found</h3>
            <p className="text-muted-foreground">
              Try adjusting your search criteria or browse all available integrations
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
