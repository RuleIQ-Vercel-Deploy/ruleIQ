'use client';
import { formatDistanceToNow } from 'date-fns';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  MoreVertical,
  Power,
  PowerOff,
  RefreshCw,
} from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

import type { Integration } from '@/lib/data/integrations-data';

interface IntegrationCardProps {
  integration: Integration;
  onConnect: (integration: Integration) => void;
  onManage: (integration: Integration) => void;
  onDisconnect: (id: string) => void;
}

const statusIcons = {
  ok: <CheckCircle2 className="h-4 w-4 text-success" />,
  error: <XCircle className="h-4 w-4 text-error" />,
  pending: <AlertCircle className="h-4 w-4 text-warning" />,
};

export function IntegrationCard({
  integration,
  onConnect,
  onManage,
  onDisconnect,
}: IntegrationCardProps) {
  const { name, logo: Icon, description, isConnected } = integration;
  const lastSync = 'lastSync' in integration ? integration.lastSync : undefined;
  const syncStatus = 'syncStatus' in integration ? integration.syncStatus : undefined;

  return (
    <Card className="bg-oxford-blue/30 border-oxford-blue/50 text-eggshell-white flex flex-col">
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="bg-eggshell-white/10 rounded-lg p-3">
            <Icon className="h-6 w-6 text-gold" />
          </div>
          <div>
            <CardTitle className="text-eggshell-white text-lg font-bold">{name}</CardTitle>
            <Badge variant={isConnected ? 'approved' : 'pending'} className="mt-1">
              {isConnected ? 'Connected' : 'Not Connected'}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow">
        <CardDescription className="text-grey-300">{description}</CardDescription>
        {isConnected && lastSync && syncStatus && (
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-grey-400">Last Sync:</span>
              <span className="font-medium">
                {formatDistanceToNow(new Date(lastSync), { addSuffix: true })}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-grey-400">Status:</span>
              <div className="flex items-center gap-2">
                {statusIcons[syncStatus as keyof typeof statusIcons]}
                <span
                  className={cn(
                    'font-medium capitalize',
                    syncStatus === 'ok' && 'text-success',
                    syncStatus === 'error' && 'text-error',
                  )}
                >
                  {syncStatus === 'ok' ? 'Successful' : 'Failed'}
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="bg-oxford-blue/20 mt-auto px-6 py-4">
        {isConnected ? (
          <div className="flex w-full items-center justify-between">
            <Button variant="ghost" size="sm" onClick={() => alert('Syncing now...')}>
              <RefreshCw className="mr-2" />
              Sync Now
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="secondary" size="sm">
                  Manage
                  <MoreVertical className="ml-2" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                className="bg-oxford-blue text-eggshell-white border-gold/50"
              >
                <DropdownMenuItem onClick={() => onManage(integration)}>
                  <AlertCircle className="mr-2" />
                  View Activity
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => onDisconnect(integration.id)}
                  className="text-error focus:bg-error/20 focus:text-error"
                >
                  <PowerOff className="mr-2" />
                  Disconnect
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        ) : (
          <Button variant="secondary" className="w-full" onClick={() => onConnect(integration)}>
            <Power className="mr-2" />
            Connect
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
