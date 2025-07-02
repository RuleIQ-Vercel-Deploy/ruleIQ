import { CheckCircle2, Shield, XCircle } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { permissions, roles } from "@/lib/data/team-data"

import type React from "react"

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
          <Table className="min-w-full divide-y divide-oxford-blue/10">
            <thead className="bg-eggshell-white/80">
              <tr>
                <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-oxford-blue sm:pl-6">
                  Permission
                </th>
                {roles.map((role) => (
                  <th
                    key={role.value}
                    scope="col"
                    className="px-3 py-3.5 text-center text-sm font-semibold text-oxford-blue"
                  >
                    {role.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-oxford-blue/10 bg-eggshell-white/50">
              {permissions.map((permission) => (
                <tr key={permission.id}>
                  <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-oxford-blue sm:pl-6">
                    {permission.feature}
                  </td>
                  {roles.map((role) => (
                    <td key={role.value} className="whitespace-nowrap px-3 py-4 text-sm text-center">
                      {permission.roles[role.value] ? (
                        <CheckCircle2 className="h-5 w-5 text-success mx-auto" />
                      ) : (
                        <XCircle className="h-5 w-5 text-stone-400 mx-auto" />
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
  )
}

// A simple Table component to be used within the card
function Table({ className, ...props }: React.HTMLAttributes<HTMLTableElement>) {
  return <table className={className} {...props} />
}
