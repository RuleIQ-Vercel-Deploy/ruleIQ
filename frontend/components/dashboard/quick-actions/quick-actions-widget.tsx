"use client";

import { ArrowRight, FileText, Shield, Upload, MessageSquare, Bot } from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/lib/stores/auth.store";
import { cn } from "@/lib/utils";


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
    label: "Compliance Wizard",
    icon: Bot,
    href: "/compliance-wizard",
    color: "bg-gold/10 text-gold-dark hover:bg-gold/20",
    description: "AI assessment",
    requiresProfile: false,
  },
  {
    label: "New Assessment",
    icon: Shield,
    href: "/assessments/new",
    color: "bg-blue-50 text-blue-600 hover:bg-blue-100",
    description: "Start compliance check",
    requiresProfile: true,
  },
  {
    label: "Generate Policy",
    icon: FileText,
    href: "/policies/generate",
    color: "bg-green-50 text-green-600 hover:bg-green-100",
    description: "Create new policy",
    requiresProfile: true,
  },
  {
    label: "Upload Evidence",
    icon: Upload,
    href: "/evidence?action=upload",
    color: "bg-purple-50 text-purple-600 hover:bg-purple-100",
    description: "Add documents",
  },
  {
    label: "Ask IQ",
    icon: MessageSquare,
    href: "/chat",
    color: "bg-indigo-50 text-indigo-600 hover:bg-indigo-100",
    description: "Get instant help",
  },
];

export function QuickActionsWidget() {
  const router = useRouter();
  const { user } = useAuthStore();
  const hasProfile = user?.businessProfile?.id;

  const handleAction = (item: QuickActionItem) => {
    if (item.requiresProfile && !hasProfile) {
      toast.error("Complete your business profile first", {
        description: "This action requires a completed business profile",
        action: {
          label: "Complete Profile",
          onClick: () => router.push("/business-profile"),
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
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="text-lg font-semibold">Quick Actions</CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/dashboard")}
          className="text-xs"
        >
          View All
          <ArrowRight className="ml-1 h-3 w-3" />
        </Button>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
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
                  "group relative p-4 rounded-lg border transition-all duration-200",
                  "hover:shadow-md",
                  "focus:outline-none focus:ring-2 focus:ring-gold/20",
                  isFeatured ? "border-gold/30 hover:border-gold/50" : "border-neutral-light hover:border-gold/20",
                  isDisabled && "opacity-50 cursor-not-allowed hover:shadow-none"
                )}
              >
                <div className="flex flex-col items-center text-center space-y-2">
                  <div className={cn("p-3 rounded-lg transition-colors", item.color)}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="font-medium text-sm text-gray-900">{item.label}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{item.description}</p>
                  </div>
                </div>
                
                {/* Hover effect */}
                {!isDisabled && (
                  <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-gold/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                )}
              </button>
            );
          })}
        </div>

        {/* Profile completion prompt */}
        {!hasProfile && (
          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-xs text-amber-800">
              Complete your business profile to unlock all quick actions
            </p>
            <Button
              size="sm"
              variant="outline"
              className="mt-2 h-7 text-xs border-amber-300 text-amber-700 hover:bg-amber-100"
              onClick={() => router.push("/business-profile")}
            >
              Complete Profile
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}