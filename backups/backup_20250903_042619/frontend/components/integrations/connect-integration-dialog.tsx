'use client';

import { Check, Power } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';

import type { Integration } from '@/lib/data/integrations-data';

interface ConnectIntegrationDialogProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  integration: Integration | null;
  onConfirm: () => void;
}

export function ConnectIntegrationDialog({
  isOpen,
  onOpenChange,
  integration,
  onConfirm,
}: ConnectIntegrationDialogProps) {
  if (!integration) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="bg-oxford-blue text-eggshell-white border-gold/50">
        <DialogHeader>
          <DialogTitle className="text-2xl text-gold">Connect to {integration.name}</DialogTitle>
          <DialogDescription className="text-grey-300">
            By connecting, you allow ruleIQ to access the following information from your{' '}
            {integration.name} account.
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <h3 className="text-eggshell-white mb-2 font-semibold">Permissions Required:</h3>
          <ul className="space-y-2">
            {(integration as any).permissions?.map((permission: string) => (
              <li key={permission} className="flex items-start gap-3">
                <Check className="mt-0.5 h-5 w-5 text-success" />
                <span className="text-grey-300">{permission}</span>
              </li>
            ))}
          </ul>
        </div>
        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button variant="secondary" onClick={onConfirm}>
            <Power className="mr-2" />
            Authorize & Connect
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
