import { CheckCircle2, Shield, XCircle } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { permissions, roles } from '@/lib/data/team-data';

import type React from 'react';

export function PermissionMatrixCard() {
  return (
    <Card className="bg-eggshell-white/90 border-oxford-blue/20 text-oxford-blue">
      <CardHeader>
        <CardTitle className="text-oxford-blue flex items-center gap-2">
          <Shield className="h-5 w-5" />
          Role Permissions
        </CardTitle>
        <CardDescription className="text-oxford-blue/80">
          A summary of permissions for each role in your organization.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table className="divide-oxford-blue/10 min-w-full divide-y">
            <thead className="bg-eggshell-white/80">
              <tr>
                <th
                  scope="col"
                  className="text-oxford-blue py-3.5 pl-4 pr-3 text-left text-sm font-semibold sm:pl-6"
                >
                  Permission
                </th>
                {roles.map((role) => (
                  <th
                    key={role.value}
                    scope="col"
                    className="text-oxford-blue px-3 py-3.5 text-center text-sm font-semibold"
                  >
                    {role.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-oxford-blue/10 bg-eggshell-white/50 divide-y">
              {permissions.map((permission) => (
                <tr key={permission.id}>
                  <td className="text-oxford-blue whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium sm:pl-6">
                    {permission.feature}
                  </td>
                  {roles.map((role) => (
                    <td
                      key={role.value}
                      className="whitespace-nowrap px-3 py-4 text-center text-sm"
                    >
                      {permission.roles[role.value] ? (
                        <CheckCircle2 className="mx-auto h-5 w-5 text-success" />
                      ) : (
                        <XCircle className="mx-auto h-5 w-5 text-stone-400" />
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

// A simple Table component to be used within the card
function Table({ className, ...props }: React.HTMLAttributes<HTMLTableElement>) {
  return <table className={className} {...props} />;
}
