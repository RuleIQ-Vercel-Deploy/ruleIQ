import { format } from 'date-fns';
import { CheckCircle2, XCircle, Info } from 'lucide-react';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';

import type { Integration, ActivityLog } from '@/lib/data/integrations-data';

interface ManageIntegrationDialogProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  integration: Integration | null;
}

const statusIcons = {
  ok: <CheckCircle2 className="h-5 w-5 text-success" />,
  error: <XCircle className="h-5 w-5 text-error" />,
  info: <Info className="h-5 w-5 text-blue-400" />,
};

function ActivityLogItem({ item }: { item: ActivityLog }) {
  return (
    <div className="flex items-start gap-4 py-3">
      <div className="mt-1">{statusIcons[item.status as keyof typeof statusIcons]}</div>
      <div className="flex-grow">
        <p className="text-eggshell-white font-medium">{item.action}</p>
        <p className="text-grey-400 text-sm">
          {format(new Date(item.timestamp), "MMM d, yyyy 'at' h:mm a")}
          {item.user && ` by ${item.user}`}
        </p>
      </div>
    </div>
  );
}

export function ManageIntegrationDialog({
  isOpen,
  onOpenChange,
  integration,
}: ManageIntegrationDialogProps) {
  if (!integration) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="bg-oxford-blue text-eggshell-white max-w-2xl border-gold/50">
        <DialogHeader>
          <DialogTitle className="text-2xl text-gold">{integration.name} Activity Log</DialogTitle>
          <DialogDescription className="text-grey-300">
            Recent events and sync history for this integration.
          </DialogDescription>
        </DialogHeader>
        <div className="mt-4 max-h-[60vh] overflow-y-auto pr-2">
          <div className="divide-oxford-blue/50 divide-y">
            {(integration as any).activity?.map((item: any) => (
              <ActivityLogItem key={item.id} item={item} />
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
