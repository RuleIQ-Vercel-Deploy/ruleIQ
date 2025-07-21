import { Mail, Send, Trash2 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { pendingInvitations, roles } from '@/lib/data/team-data';

export function PendingInvitationsTable() {
  return (
    <Card className="bg-eggshell-white/90 border-oxford-blue/20 text-oxford-blue">
      <CardHeader>
        <CardTitle className="text-oxford-blue flex items-center gap-2">
          <Mail className="h-5 w-5" />
          Pending Invitations
        </CardTitle>
        <CardDescription className="text-oxford-blue/80">
          These users have been invited but have not yet joined the team.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flow-root">
          <ul role="list" className="divide-oxford-blue/10 -my-4 divide-y">
            {pendingInvitations.map((invitation) => {
              const roleInfo = roles.find((r) => r.value === invitation.role);
              return (
                <li key={invitation.id} className="flex items-center justify-between gap-x-6 py-4">
                  <div className="min-w-0">
                    <p className="text-oxford-blue text-sm font-semibold leading-6">
                      {invitation.email}
                    </p>
                    <p className="text-oxford-blue/70 mt-1 flex items-center gap-1.5 text-xs leading-5">
                      {roleInfo && <roleInfo.icon className="h-3.5 w-3.5" />}
                      Invited as {invitation.role}
                    </p>
                  </div>
                  <div className="flex flex-none items-center gap-x-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-oxford-blue/80 hover:text-oxford-blue"
                    >
                      <Send className="mr-1.5 h-3.5 w-3.5" />
                      Resend
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-error/80 hover:bg-error/10 hover:text-error"
                    >
                      <span className="sr-only">Revoke</span>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
