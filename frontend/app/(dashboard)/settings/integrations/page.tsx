'use client';

import * as React from 'react';

import { DashboardHeader } from '@/components/dashboard/dashboard-header';
import { ConnectIntegrationDialog } from '@/components/integrations/connect-integration-dialog';
import { IntegrationCard } from '@/components/integrations/integration-card';
import { ManageIntegrationDialog } from '@/components/integrations/manage-integration-dialog';
import { AppSidebar } from '@/components/navigation/app-sidebar';
import {
  integrations as initialIntegrations,
  type Integration,
} from '@/lib/data/integrations-data';

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = React.useState(initialIntegrations);
  const [isConnectModalOpen, setConnectModalOpen] = React.useState(false);
  const [isManageModalOpen, setManageModalOpen] = React.useState(false);
  const [selectedIntegration, setSelectedIntegration] = React.useState<Integration | null>(null);

  const handleConnect = (integration: Integration) => {
    setSelectedIntegration(integration);
    setConnectModalOpen(true);
  };

  const handleManage = (integration: Integration) => {
    setSelectedIntegration(integration);
    setManageModalOpen(true);
  };

  const handleConfirmConnect = () => {
    if (selectedIntegration) {
      setIntegrations((prev) =>
        prev.map((integ) =>
          integ.id === selectedIntegration.id
            ? {
                id: integ.id,
                name: integ.name,
                logo: integ.logo,
                description: integ.description,
                isConnected: true as const,
                lastSync: new Date().toISOString(),
                syncStatus: 'ok',
                activity: [],
              }
            : integ,
        ),
      );
    }
    setConnectModalOpen(false);
    setSelectedIntegration(null);
  };

  const handleDisconnect = (id: string) => {
    setIntegrations((prev) =>
      prev.map((integ) =>
        integ.id === id
          ? {
              id: integ.id,
              name: integ.name,
              logo: integ.logo,
              description: integ.description,
              isConnected: false as const,
              permissions: [],
            }
          : integ,
      ),
    );
  };

  return (
    <div className="bg-midnight-blue flex min-h-screen w-full">
      <AppSidebar />
      <div className="flex flex-1 flex-col">
        <DashboardHeader />
        <main className="flex-1 p-6">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {integrations.map((integration) => (
              <IntegrationCard
                key={integration.id}
                integration={integration}
                onConnect={handleConnect}
                onManage={handleManage}
                onDisconnect={handleDisconnect}
              />
            ))}
          </div>
        </main>
      </div>
      <ConnectIntegrationDialog
        isOpen={isConnectModalOpen}
        onOpenChange={setConnectModalOpen}
        integration={selectedIntegration}
        onConfirm={handleConfirmConnect}
      />
      <ManageIntegrationDialog
        isOpen={isManageModalOpen}
        onOpenChange={setManageModalOpen}
        integration={selectedIntegration}
      />
    </div>
  );
}
