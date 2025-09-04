import { Shield, Eye, Edit } from 'lucide-react';

import type { LucideIcon } from 'lucide-react';

export type Role = 'Admin' | 'Member' | 'Viewer';
export type Status = 'Active' | 'Inactive' | 'Pending';

export interface TeamMember {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: Role;
  status: Status;
  lastActive: string;
}

export interface Invitation {
  id: string;
  email: string;
  role: Role;
  invitedAt: string;
}

export interface Permission {
  id: string;
  feature: string;
  description: string;
  roles: {
    Admin: boolean;
    Member: boolean;
    Viewer: boolean;
  };
}

export const teamMembers: TeamMember[] = [
  {
    id: 'usr-001',
    name: 'Alex Johnson',
    email: 'alex.j@example.com',
    avatar: '/placeholder.svg?height=40&width=40',
    role: 'Admin',
    status: 'Active',
    lastActive: '2 hours ago',
  },
  {
    id: 'usr-002',
    name: 'Maria Garcia',
    email: 'maria.g@example.com',
    avatar: '/placeholder.svg?height=40&width=40',
    role: 'Member',
    status: 'Active',
    lastActive: '1 day ago',
  },
  {
    id: 'usr-003',
    name: 'James Smith',
    email: 'james.s@example.com',
    avatar: '/placeholder.svg?height=40&width=40',
    role: 'Member',
    status: 'Inactive',
    lastActive: '1 week ago',
  },
  {
    id: 'usr-004',
    name: 'Patricia Williams',
    email: 'patricia.w@example.com',
    avatar: '/placeholder.svg?height=40&width=40',
    role: 'Viewer',
    status: 'Active',
    lastActive: '30 minutes ago',
  },
  {
    id: 'usr-005',
    name: 'Robert Brown',
    email: 'robert.b@example.com',
    avatar: '/placeholder.svg?height=40&width=40',
    role: 'Viewer',
    status: 'Active',
    lastActive: '5 hours ago',
  },
];

export const pendingInvitations: Invitation[] = [
  {
    id: 'inv-001',
    email: 'new.user@example.com',
    role: 'Member',
    invitedAt: '2 days ago',
  },
  {
    id: 'inv-002',
    email: 'another.user@example.com',
    role: 'Viewer',
    invitedAt: '5 days ago',
  },
];

export const roles: { value: Role; label: string; icon: LucideIcon }[] = [
  { value: 'Admin', label: 'Admin', icon: Shield },
  { value: 'Member', label: 'Member', icon: Edit },
  { value: 'Viewer', label: 'Viewer', icon: Eye },
];

export const permissions: Permission[] = [
  {
    id: 'perm-001',
    feature: 'Assessments',
    description: 'Can view, create, and manage compliance assessments.',
    roles: { Admin: true, Member: true, Viewer: false },
  },
  {
    id: 'perm-002',
    feature: 'Evidence',
    description: 'Can view, upload, and manage evidence.',
    roles: { Admin: true, Member: true, Viewer: false },
  },
  {
    id: 'perm-003',
    feature: 'Policies',
    description: 'Can view, create, and manage policies.',
    roles: { Admin: true, Member: true, Viewer: false },
  },
  {
    id: 'perm-004',
    feature: 'Reports',
    description: 'Can view and export compliance reports.',
    roles: { Admin: true, Member: true, Viewer: true },
  },
  {
    id: 'perm-005',
    feature: 'Team Management',
    description: 'Can invite, remove, and manage team members and roles.',
    roles: { Admin: true, Member: false, Viewer: false },
  },
  {
    id: 'perm-006',
    feature: 'Billing',
    description: 'Can manage subscription and view billing history.',
    roles: { Admin: true, Member: false, Viewer: false },
  },
];
