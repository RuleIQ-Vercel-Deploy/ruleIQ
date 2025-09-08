'use client';

import { ArrowRight, FileText, Shield, Upload, MessageSquare, Bot } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuthStore } from '@/lib/stores/auth.store';
import { cn } from '@/lib/utils';

interface QuickActionItem {
  label: string;
  icon: React.ElementType;
  href?: string;
  action?: () => void;
  color: string;
  description: string;
  requiresProfile?: boolean;
}

const actions: QuickActionItem[] = [
  {
    label: 'Compliance Wizard',
    icon: Bot,
    href: '/compliance-wizard',
    color: 'bg-warning/10 text-warning hover:bg-warning/20',
    description: 'AI assessment',
    requiresProfile: false,
  },
  {
    label: 'New Assessment',
    icon: Shield,
    href: '/assessments/new',
    color: 'bg-primary/10 text-primary hover:bg-primary/20',
    description: 'Start compliance check',
    requiresProfile: true,
  },
  {
    label: 'Generate Policy',
    icon: FileText,
    href: '/policies/generate',
    color: 'bg-secondary/10 text-secondary hover:bg-secondary/20',
    description: 'Create new policy',
    requiresProfile: true,
  },
  {
    label: 'Upload Evidence',
    icon: Upload,
    href: '/evidence?action=upload',
    color: 'bg-primary/10 text-primary hover:bg-primary/20',
    description: 'Add documents',
  },
  {
    label: 'Ask IQ',
    icon: MessageSquare,
    href: '/chat',
    color: 'bg-primary/10 text-primary hover:bg-primary/20',
    description: 'Get instant help',
  },
];

export function QuickActionsWidget() {
  const router = useRouter();
  const { user } = useAuthStore();
  const hasProfile = user?.businessProfile?.id;

  const handleAction = (item: QuickActionItem) => {
    if (item.requiresProfile && !hasProfile) {
      toast.error('Complete your business profile first', {
        description: 'This action requires a completed business profile',
        action: {
          label: 'Complete Profile',
          onClick: () => router.push('/business-profile'),
        },
      });
      return;
    }

    if (item.href) {
      router.push(item.href);
    } else if (item.action) {
      item.action();
    }
  };

  return (
    <Card className="glass-card h-full">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="gradient-text text-lg font-semibold">Quick Actions</CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/dashboard')}
          className="text-xs hover:bg-glass-white"
        >
          View All
          <ArrowRight className="ml-1 h-3 w-3" />
        </Button>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-5">
          {actions.map((item, index) => {
            const Icon = item.icon;
            const isDisabled = item.requiresProfile && !hasProfile;
            const isFeatured = index === 0; // First item (Compliance Wizard) is featured

            return (
              <button
                key={item.label}
                onClick={() => handleAction(item)}
                disabled={isDisabled}
                className={cn(
                  'group relative rounded-lg border p-4 transition-all duration-200',
                  'bg-glass-white hover:bg-glass-white-hover hover:shadow-md',
                  'focus:outline-none focus:ring-2 focus:ring-primary/20',
                  isFeatured
                    ? 'border-warning/30 hover:border-warning/50'
                    : 'border-glass-border hover:border-glass-border-hover',
                  isDisabled && 'cursor-not-allowed opacity-50 hover:shadow-none',
                )}
              >
                <div className="flex flex-col items-center space-y-2 text-center">
                  <div className={cn('rounded-lg p-3 transition-colors', item.color)}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">{item.label}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{item.description}</p>
                  </div>
                </div>

                {/* Hover effect */}
                {!isDisabled && (
                  <div className="pointer-events-none absolute inset-0 rounded-lg bg-gradient-to-br from-gold/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                )}
              </button>
            );
          })}
        </div>

        {/* Profile completion prompt */}
        {!hasProfile && (
          <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3">
            <p className="text-xs text-amber-800">
              Complete your business profile to unlock all quick actions
            </p>
            <Button
              size="sm"
              variant="outline"
              className="mt-2 h-7 border-amber-300 text-xs text-amber-700 hover:bg-amber-100"
              onClick={() => router.push('/business-profile')}
            >
              Complete Profile
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
