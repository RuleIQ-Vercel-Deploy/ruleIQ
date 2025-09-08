'use client';

import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  FileText,
  Shield,
  Upload,
  MessageSquare,
  X,
  Zap,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { toast } from 'sonner';

import { useAuthStore } from '@/lib/stores/auth.store';
import { cn } from '@/lib/utils';

interface QuickAction {
  id: string;
  label: string;
  description: string;
  icon: React.ElementType;
  href?: string;
  action?: () => void;
  color: string;
  requiresProfile?: boolean;
}

const quickActions: QuickAction[] = [
  {
    id: 'new-assessment',
    label: 'Start Assessment',
    description: 'Quick compliance check',
    icon: Shield,
    href: '/assessments/new',
    color: 'text-cyan',
    requiresProfile: true,
  },
  {
    id: 'generate-policy',
    label: 'Generate Policy',
    description: 'AI-powered policy creation',
    icon: FileText,
    href: '/policies/generate',
    color: 'text-gold',
    requiresProfile: true,
  },
  {
    id: 'upload-evidence',
    label: 'Upload Evidence',
    description: 'Add compliance documents',
    icon: Upload,
    href: '/evidence?action=upload',
    color: 'text-green-600',
  },
  {
    id: 'ask-iq',
    label: 'Ask IQ Assistant',
    description: 'Get instant compliance help',
    icon: MessageSquare,
    href: '/chat',
    color: 'text-blue-600',
  },
  {
    id: 'quick-scan',
    label: 'Quick Scan',
    description: 'Rapid compliance check',
    icon: Zap,
    action: () => {
      toast.success('Quick scan started', {
        description: "We'll analyze your current compliance status",
      });
    },
    color: 'text-teal-600',
    requiresProfile: true,
  },
];

export function QuickActionsPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();
  const { user } = useAuthStore();
  const hasProfile = user?.businessProfile?.id;

  const handleAction = (action: QuickAction) => {
    if (action.requiresProfile && !hasProfile) {
      toast.error('Complete your business profile first', {
        description: 'This action requires a completed business profile',
        action: {
          label: 'Complete Profile',
          onClick: () => router.push('/business-profile'),
        },
      });
      return;
    }

    if (action.href) {
      router.push(action.href);
    } else if (action.action) {
      action.action();
    }
    setIsOpen(false);
  };

  return (
    <>
      {/* Floating Action Button */}
      <motion.div
        className="fixed bottom-8 right-8 z-50"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2 }}
      >
        <motion.button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'group relative h-14 w-14 rounded-full bg-gradient-to-br from-gold to-gold-dark text-primary shadow-lg transition-all duration-200',
            'hover:shadow-xl hover:shadow-gold/25',
            'focus:outline-none focus:ring-4 focus:ring-gold/20',
            isOpen && 'rotate-45',
          )}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          animate={{ rotate: isOpen ? 45 : 0 }}
        >
          <Plus className="absolute inset-0 m-auto h-6 w-6" />

          {/* Pulse animation */}
          <span className="absolute inset-0 animate-ping rounded-full bg-gold opacity-20" />

          {/* Sparkle effect */}
          <Sparkles className="text-cyan absolute -right-1 -top-1 h-4 w-4 animate-pulse" />
        </motion.button>
      </motion.div>

      {/* Actions Panel */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm"
            />

            {/* Panel */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              className="border-neutral-light fixed bottom-28 right-8 z-50 w-80 overflow-hidden rounded-xl border bg-white shadow-2xl"
            >
              {/* Header */}
              <div className="to-primary-dark bg-gradient-to-r from-primary p-4 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold">Quick Actions</h3>
                    <p className="text-sm text-white/80">Get things done faster</p>
                  </div>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="rounded-lg p-1 transition-colors hover:bg-white/10"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Actions List */}
              <div className="p-2">
                {quickActions.map((action, index) => {
                  const Icon = action.icon;
                  const isDisabled = action.requiresProfile && !hasProfile;

                  return (
                    <motion.button
                      key={action.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => handleAction(action)}
                      disabled={isDisabled}
                      className={cn(
                        'group w-full rounded-lg p-3 text-left transition-all duration-200',
                        'hover:bg-gray-50 hover:shadow-sm',
                        'focus:outline-none focus:ring-2 focus:ring-gold/20',
                        isDisabled && 'cursor-not-allowed opacity-50',
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={cn(
                            'rounded-lg bg-gray-50 p-2 transition-colors',
                            !isDisabled && 'group-hover:bg-white',
                            action.color,
                          )}
                        >
                          <Icon className="h-5 w-5" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="font-medium text-gray-900">{action.label}</div>
                          <div className="truncate text-sm text-gray-500">{action.description}</div>
                        </div>
                        <ChevronRight
                          className={cn(
                            'h-4 w-4 text-gray-400 transition-transform',
                            !isDisabled && 'group-hover:translate-x-1',
                          )}
                        />
                      </div>
                    </motion.button>
                  );
                })}
              </div>

              {/* Footer Tip */}
              <div className="border-t border-gray-100 bg-gray-50 p-4">
                <p className="text-center text-xs text-gray-600">
                  Press <kbd className="rounded border bg-white px-1.5 py-0.5 text-xs">⌘K</kbd> for
                  command palette
                </p>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
