"use client"

import { useEffect, useState } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import { useMutation } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { LoadingLayout } from "@/components/layout/loading-layout"
import { integrationsApi } from "@/api/integrations"
import { CheckCircle, AlertCircle, ArrowLeft } from "lucide-react"
import { toast } from "@/hooks/use-toast"

interface OAuthHandlerProps {
  providerId: string
  providerName: string
}

export function OAuthHandler({ providerId, providerName }: OAuthHandlerProps) {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState<"processing" | "success" | "error">("processing")
  const [errorMessage, setErrorMessage] = useState<string>("")

  const completeOAuthMutation = useMutation({
    mutationFn: ({ code, state }: { code: string; state?: string }) =>
      integrationsApi.completeOAuth(providerId, code, state),
    onSuccess: (integration) => {
      setStatus("success")
      toast({
        title: "Integration connected successfully",
        description: `${providerName} has been connected to your account.`,
      })
      // Redirect to integration details after a short delay
      setTimeout(() => {
        navigate(`/app/integrations/${integration.id}`)
      }, 2000)
    },
    onError: (error: any) => {
      setStatus("error")
      setErrorMessage(error.response?.data?.detail || "Failed to complete OAuth flow")
      toast({
        title: "Integration failed",
        description: "There was an error connecting your integration.",
        variant: "destructive",
      })
    },
  })

  useEffect(() => {
    const code = searchParams.get("code")
    const state = searchParams.get("state")
    const error = searchParams.get("error")
    const errorDescription = searchParams.get("error_description")

    if (error) {
      setStatus("error")
      setErrorMessage(errorDescription || error)
      return
    }

    if (code) {
      completeOAuthMutation.mutate({ code, state: state || undefined })
    } else {
      setStatus("error")
      setErrorMessage("No authorization code received")
    }
  }, [searchParams])

  if (status === "processing") {
    return <LoadingLayout />
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4">
            {status === "success" ? (
              <CheckCircle className="h-16 w-16 text-green-500" />
            ) : (
              <AlertCircle className="h-16 w-16 text-red-500" />
            )}
          </div>
          <CardTitle>{status === "success" ? "Integration Connected!" : "Connection Failed"}</CardTitle>
          <CardDescription>
            {status === "success"
              ? `${providerName} has been successfully connected to your account.`
              : "There was an error connecting your integration."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {status === "error" && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          <div className="flex flex-col space-y-2">
            {status === "success" ? (
              <p className="text-sm text-muted-foreground text-center">Redirecting to integration settings...</p>
            ) : (
              <div className="flex flex-col space-y-2">
                <Button onClick={() => navigate(`/app/integrations/setup/${providerId}`)} className="w-full">
                  Try Again
                </Button>
                <Button variant="outline" onClick={() => navigate("/app/integrations")} className="w-full">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Integrations
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
