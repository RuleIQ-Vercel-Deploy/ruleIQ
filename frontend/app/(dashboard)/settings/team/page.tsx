import { Users } from "lucide-react"

import { InviteMemberDialog } from "@/components/team/invite-member-dialog"
import { PendingInvitationsTable } from "@/components/team/pending-invitations-table"
import { PermissionMatrixCard } from "@/components/team/permission-matrix-card"
import { columns } from "@/components/team/team-members-columns"
import { TeamMembersTable } from "@/components/team/team-members-table"
import { teamMembers } from "@/lib/data/team-data"


export default function TeamManagementPage() {
  return (
    <div className="min-h-screen w-full bg-oxford-blue text-eggshell-white p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-eggshell-white flex items-center gap-3">
              <Users className="h-8 w-8" />
              Team Management
            </h1>
            <p className="text-eggshell-white/70 mt-1">Manage your team members, roles, and permissions.</p>
          </div>
          <InviteMemberDialog />
        </header>

        <main className="space-y-8">
          <section>
            <h2 className="text-xl font-semibold text-eggshell-white mb-4">Active Team Members</h2>
            <TeamMembersTable columns={columns} data={teamMembers} />
          </section>

          <section>
            <PendingInvitationsTable />
          </section>

          <section>
            <PermissionMatrixCard />
          </section>
        </main>
      </div>
    </div>
  )
}
