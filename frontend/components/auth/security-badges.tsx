import { Shield, Lock, CheckCircle, Globe } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface SecurityBadgesProps {
  className?: string;
  variant?: 'default' | 'compact';
}

export function SecurityBadges({ className, variant = 'default' }: SecurityBadgesProps) {
  const badges = [
    {
      icon: Lock,
      text: '256-bit SSL',
      description: 'Bank-level encryption',
    },
    {
      icon: Shield,
      text: 'GDPR Compliant',
      description: 'Privacy by design',
    },
    {
      icon: CheckCircle,
      text: 'ISO 27001',
      description: 'Security certified',
    },
    {
      icon: Globe,
      text: 'SOC 2 Type II',
      description: 'Audited security',
    },
  ];

  if (variant === 'compact') {
    return (
      <div className={cn('flex flex-wrap justify-center gap-2', className)}>
        {badges.map((badge, index) => {
          const Icon = badge.icon;
          return (
            <Badge
              key={index}
              variant="secondary"
              className="flex items-center gap-1.5 border-turquoise/20 bg-turquoise/5 px-3 py-1.5 text-xs text-turquoise"
            >
              <Icon className="h-3 w-3" />
              {badge.text}
            </Badge>
          );
        })}
      </div>
    );
  }

  return (
    <div className={cn('grid grid-cols-2 gap-6', className)}>
      {badges.map((badge, index) => {
        const Icon = badge.icon;
        return (
          <div key={index} className="flex items-center gap-3 text-sm">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-turquoise/20 bg-turquoise/10">
              <Icon className="h-5 w-5 text-navy" />
            </div>
            <div>
              <div className="font-semibold text-foreground">{badge.text}</div>
              <div className="text-xs leading-relaxed text-muted-foreground">
                {badge.description}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

interface TrustSignalsProps {
  className?: string;
}

export function TrustSignals({ className }: TrustSignalsProps) {
  return (
    <div className={cn('space-y-6', className)}>
      <div className="text-left">
        <h3 className="mb-3 text-2xl font-bold text-foreground">Why Choose ruleIQ?</h3>
        <p className="text-base leading-relaxed text-muted-foreground">
          Trusted by compliance professionals worldwide
        </p>
      </div>

      <SecurityBadges />

      <div className="space-y-4 text-sm">
        <div className="flex items-start gap-4">
          <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-success" />
          <div>
            <div className="font-semibold text-foreground">Enterprise Security</div>
            <div className="leading-relaxed text-muted-foreground">
              Your data is protected with military-grade encryption
            </div>
          </div>
        </div>

        <div className="flex items-start gap-4">
          <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-success" />
          <div>
            <div className="font-semibold text-foreground">Compliance Ready</div>
            <div className="leading-relaxed text-muted-foreground">
              Built by compliance experts for compliance professionals
            </div>
          </div>
        </div>

        <div className="flex items-start gap-4">
          <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-success" />
          <div>
            <div className="font-semibold text-foreground">24/7 Support</div>
            <div className="leading-relaxed text-muted-foreground">
              Expert support when you need it most
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-border/50 pt-6">
        <div className="flex items-center justify-start gap-6 text-sm text-muted-foreground">
          <span className="flex items-center gap-2">🔒 Secure</span>
          <span className="flex items-center gap-2">🛡️ Private</span>
          <span className="flex items-center gap-2">✅ Compliant</span>
        </div>
      </div>
    </div>
  );
}
