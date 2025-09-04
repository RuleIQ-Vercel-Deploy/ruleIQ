import { Users } from 'lucide-react';

import { InviteMemberDialog } from '@/components/team/invite-member-dialog';
import { PendingInvitationsTable } from '@/components/team/pending-invitations-table';
import { PermissionMatrixCard } from '@/components/team/permission-matrix-card';
import { columns } from '@/components/team/team-members-columns';
import { TeamMembersTable } from '@/components/team/team-members-table';
import { teamMembers } from '@/lib/data/team-data';

export default function TeamManagementPage() {
  return (
    <div className="bg-oxford-blue text-eggshell-white min-h-screen w-full p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-eggshell-white flex items-center gap-3 text-3xl font-bold">
              <Users className="h-8 w-8" />
              Team Management
            </h1>
            <p className="text-eggshell-white/70 mt-1">
              Manage your team members, roles, and permissions.
            </p>
          </div>
          <InviteMemberDialog />
        </header>

        <main className="space-y-8">
          <section>
            <h2 className="text-eggshell-white mb-4 text-xl font-semibold">Active Team Members</h2>
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
  );
}
