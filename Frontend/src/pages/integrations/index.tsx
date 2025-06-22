import { Routes, Route } from "react-router-dom"
import { IntegrationsDashboard } from "./integrations-dashboard"
import { IntegrationMarketplace } from "./integration-marketplace"
import { IntegrationSetup } from "./integration-setup"
import { IntegrationDetails } from "./integration-details"
import { OAuthHandler } from "@/components/integrations/oauth-handler"

export function IntegrationsRoutes() {
  return (
    <Routes>
      <Route index element={<IntegrationsDashboard />} />
      <Route path="marketplace" element={<IntegrationMarketplace />} />
      <Route path="setup/:providerId" element={<IntegrationSetup />} />
      <Route path=":integrationId" element={<IntegrationDetails />} />
      <Route path="oauth/callback/:providerId" element={<OAuthHandler providerId={""} providerName={""} />} />
    </Routes>
  )
}

export default IntegrationsRoutes
