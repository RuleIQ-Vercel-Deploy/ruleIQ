"use client"

import { 
  Building2, 
  Globe, 
  Users, 
  Shield, 
  Calendar,
  MapPin,
  DollarSign,
  Database,
  Share2,
  Edit,
  CheckCircle2,
  AlertCircle
} from "lucide-react"
import * as React from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { H1, H2, H3, Body, Caption } from "@/components/ui/typography"
import { useBusinessProfileStore } from "@/lib/stores/business-profile.store"

import { ProfileWizard } from "./profile-wizard"

export function ProfileView() {
  const { profile, isLoading, isProfileComplete } = useBusinessProfileStore()
  const [isEditing, setIsEditing] = React.useState(false)

  // Calculate profile completion percentage
  const calculateCompletion = () => {
    if (!profile) return 0
    
    const fields = [
      profile.company_name,
      profile.industry,
      profile.size,
      profile.country,
      profile.compliance_frameworks?.length > 0,
      profile.data_types_collected?.length > 0,
      profile.data_storage_locations?.length > 0,
      profile.website,
      profile.description,
    ]
    
    const completed = fields.filter(Boolean).length
    return Math.round((completed / fields.length) * 100)
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {/* Loading skeleton */}
        <div className="h-8 w-48 bg-muted animate-pulse rounded" />
        <div className="grid gap-6 md:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-48 bg-muted animate-pulse rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  if (!profile || isEditing) {
    return (
      <div className="space-y-6">
        {isEditing && (
          <div className="flex items-center justify-between">
            <H1>Edit Business Profile</H1>
            <Button
              variant="outline"
              onClick={() => setIsEditing(false)}
            >
              Cancel
            </Button>
          </div>
        )}
        <ProfileWizard 
          initialData={profile || undefined}
          onComplete={() => setIsEditing(false)}
        />
      </div>
    )
  }

  const completionPercentage = calculateCompletion()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <H1>Business Profile</H1>
          <Body color="muted">Manage your company information and compliance requirements</Body>
        </div>
        <Button
          variant="outline"
          onClick={() => setIsEditing(true)}
          className="gap-2"
        >
          <Edit className="h-4 w-4" />
          Edit Profile
        </Button>
      </div>

      {/* Completion Status */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <H3>Profile Completion</H3>
                <Body color="muted">
                  {isProfileComplete 
                    ? "Your profile is complete and ready for compliance automation"
                    : "Complete your profile to unlock all features"
                  }
                </Body>
              </div>
              <div className="flex items-center gap-2">
                {isProfileComplete ? (
                  <CheckCircle2 className="h-5 w-5 text-success" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-warning" />
                )}
                <span className="text-2xl font-bold">{completionPercentage}%</span>
              </div>
            </div>
            <Progress value={completionPercentage} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Profile Information Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Company Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Company Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Caption color="muted">Company Name</Caption>
              <Body className="font-medium">{profile.company_name}</Body>
            </div>
            
            {profile.website && (
              <div>
                <Caption color="muted">Website</Caption>
                <a 
                  href={profile.website} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-cyan hover:text-cyan-light flex items-center gap-1"
                >
                  <Globe className="h-3 w-3" />
                  {profile.website}
                </a>
              </div>
            )}
            
            {profile.founded_year && (
              <div>
                <Caption color="muted">Founded</Caption>
                <Body className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  {profile.founded_year}
                </Body>
              </div>
            )}
            
            {profile.description && (
              <div>
                <Caption color="muted">Description</Caption>
                <Body className="text-sm">{profile.description}</Body>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Industry & Location */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Industry & Size
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Caption color="muted">Industry</Caption>
              <Body className="font-medium capitalize">
                {profile.industry.replace(/-/g, ' ')}
              </Body>
            </div>
            
            <div>
              <Caption color="muted">Company Size</Caption>
              <Body className="font-medium">{profile.size} employees</Body>
            </div>
            
            {profile.annual_revenue && (
              <div>
                <Caption color="muted">Annual Revenue</Caption>
                <Body className="flex items-center gap-1">
                  <DollarSign className="h-4 w-4" />
                  {profile.annual_revenue.toUpperCase()}
                </Body>
              </div>
            )}
            
            <div>
              <Caption color="muted">Location</Caption>
              <Body className="flex items-center gap-1">
                <MapPin className="h-4 w-4" />
                {profile.country}
              </Body>
            </div>
          </CardContent>
        </Card>

        {/* Compliance Frameworks */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Compliance Frameworks
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {profile.compliance_frameworks.map((framework) => (
                <Badge key={framework} variant="secondary" className="uppercase">
                  {framework}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Data Handling */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Data Handling
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {profile.data_types_collected && profile.data_types_collected.length > 0 && (
              <div>
                <Caption color="muted">Data Types Collected</Caption>
                <div className="flex flex-wrap gap-2 mt-1">
                  {profile.data_types_collected.map((type) => (
                    <Badge key={type} variant="outline" className="text-xs">
                      {type.replace(/_/g, ' ')}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            
            {profile.data_storage_locations && profile.data_storage_locations.length > 0 && (
              <div>
                <Caption color="muted">Storage Locations</Caption>
                <div className="flex flex-wrap gap-2 mt-1">
                  {profile.data_storage_locations.map((location) => (
                    <Badge key={location} variant="outline" className="text-xs">
                      {location.toUpperCase()}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            
            <div className="flex items-center gap-2">
              <Share2 className="h-4 w-4" />
              <Body className="text-sm">
                {profile.third_party_sharing 
                  ? "Shares data with third parties"
                  : "Does not share data with third parties"
                }
              </Body>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Timestamps */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <Caption>Created: {new Date(profile.created_at).toLocaleDateString()}</Caption>
        <Caption>Last updated: {new Date(profile.updated_at).toLocaleDateString()}</Caption>
      </div>
    </div>
  )
}