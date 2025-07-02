"use client";

import { Command } from "cmdk";
import {
  FileText,
  Shield,
  Upload,
  MessageSquare,
  Home,
  Settings,
  LogOut,
  Search,
  ChevronRight,
  User,
  FileCheck,
  BarChart,
  Bell,
  HelpCircle,
  Zap,
  Building,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { toast } from "sonner";

import { useAuthStore } from "@/lib/stores/auth.store";
import { cn } from "@/lib/utils";

interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon: React.ElementType;
  action: () => void;
  group: string;
  keywords?: string[];
  requiresProfile?: boolean;
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const hasProfile = user?.businessProfile?.id;

  const handleAction = useCallback((action: () => void) => {
    setOpen(false);
    // Small delay to allow dialog to close smoothly
    setTimeout(action, 100);
  }, []);

  const commands: CommandItem[] = [
    // Navigation
    {
      id: "home",
      label: "Go to Dashboard",
      icon: Home,
      action: () => router.push("/dashboard"),
      group: "Navigation",
      keywords: ["home", "dashboard"],
    },
    {
      id: "analytics",
      label: "View Analytics",
      icon: BarChart,
      action: () => router.push("/analytics"),
      group: "Navigation",
      keywords: ["data", "metrics", "stats"],
    },
    {
      id: "profile",
      label: "Business Profile",
      icon: Building,
      action: () => router.push("/business-profile"),
      group: "Navigation",
      keywords: ["company", "organization"],
    },
    {
      id: "settings",
      label: "Settings",
      icon: Settings,
      action: () => router.push("/settings"),
      group: "Navigation",
    },

    // Quick Actions
    {
      id: "new-assessment",
      label: "Start New Assessment",
      description: "Begin a compliance assessment",
      icon: Shield,
      action: () => {
        if (!hasProfile) {
          toast.error("Complete your business profile first");
          return;
        }
        router.push("/assessments/new");
      },
      group: "Quick Actions",
      keywords: ["compliance", "audit", "check"],
      requiresProfile: true,
    },
    {
      id: "generate-policy",
      label: "Generate Policy",
      description: "Create a new compliance policy",
      icon: FileText,
      action: () => {
        if (!hasProfile) {
          toast.error("Complete your business profile first");
          return;
        }
        router.push("/policies/generate");
      },
      group: "Quick Actions",
      keywords: ["document", "create"],
      requiresProfile: true,
    },
    {
      id: "upload-evidence",
      label: "Upload Evidence",
      description: "Add compliance documents",
      icon: Upload,
      action: () => router.push("/evidence?action=upload"),
      group: "Quick Actions",
      keywords: ["document", "file", "proof"],
    },
    {
      id: "chat-iq",
      label: "Ask IQ Assistant",
      description: "Get instant compliance help",
      icon: MessageSquare,
      action: () => router.push("/chat"),
      group: "Quick Actions",
      keywords: ["help", "ai", "assistant", "question"],
    },
    {
      id: "quick-scan",
      label: "Run Quick Scan",
      description: "Rapid compliance check",
      icon: Zap,
      action: () => {
        if (!hasProfile) {
          toast.error("Complete your business profile first");
          return;
        }
        toast.success("Quick scan started");
      },
      group: "Quick Actions",
      keywords: ["fast", "rapid", "scan"],
      requiresProfile: true,
    },

    // Features
    {
      id: "assessments",
      label: "View All Assessments",
      icon: Shield,
      action: () => router.push("/assessments"),
      group: "Features",
    },
    {
      id: "policies",
      label: "View All Policies",
      icon: FileText,
      action: () => router.push("/policies"),
      group: "Features",
    },
    {
      id: "evidence",
      label: "Evidence Library",
      icon: FileCheck,
      action: () => router.push("/evidence"),
      group: "Features",
    },
    {
      id: "reports",
      label: "Reports",
      icon: BarChart,
      action: () => router.push("/reports"),
      group: "Features",
    },

    // Account
    {
      id: "notifications",
      label: "Notifications",
      icon: Bell,
      action: () => toast.info("Notifications coming soon"),
      group: "Account",
    },
    {
      id: "help",
      label: "Help & Support",
      icon: HelpCircle,
      action: () => toast.info("Help center coming soon"),
      group: "Account",
    },
    {
      id: "logout",
      label: "Sign Out",
      icon: LogOut,
      action: () => {
        logout();
        router.push("/login");
      },
      group: "Account",
    },
  ];

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    const handleOpen = () => setOpen(true);
    
    document.addEventListener("keydown", down);
    document.addEventListener("openCommandPalette", handleOpen);
    
    return () => {
      document.removeEventListener("keydown", down);
      document.removeEventListener("openCommandPalette", handleOpen);
    };
  }, []);

  const groupedCommands = commands.reduce((acc, command) => {
    if (!acc[command.group]) {
      acc[command.group] = [];
    }
    acc[command.group].push(command);
    return acc;
  }, {} as Record<string, CommandItem[]>);

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      label="Command Palette"
      className="fixed inset-0 z-50"
    >
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => setOpen(false)}
      />
      <div className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl">
        <div className="overflow-hidden rounded-xl bg-white shadow-2xl border border-neutral-light">
          <Command.Input
            placeholder="Search for commands..."
            className="w-full border-0 px-6 py-4 text-base outline-none placeholder:text-gray-400 focus:ring-0"
          />
          
          <Command.List className="max-h-[400px] overflow-y-auto p-2">
            <Command.Empty className="py-12 text-center text-sm text-gray-500">
              No results found.
            </Command.Empty>

            {Object.entries(groupedCommands).map(([group, items]) => (
              <Command.Group key={group} heading={group} className="mb-3">
                <div className="px-2 py-1.5 text-xs font-medium text-gray-500">
                  {group}
                </div>
                {items.map((item) => {
                  const Icon = item.icon;
                  const isDisabled = item.requiresProfile && !hasProfile;

                  return (
                    <Command.Item
                      key={item.id}
                      value={`${item.label} ${item.keywords?.join(" ") || ""}`}
                      onSelect={() => handleAction(item.action)}
                      disabled={isDisabled}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors cursor-pointer",
                        "data-[selected]:bg-gray-100",
                        isDisabled && "opacity-50 cursor-not-allowed"
                      )}
                    >
                      <Icon className="h-4 w-4 text-gray-500" />
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">
                          {item.label}
                        </div>
                        {item.description && (
                          <div className="text-xs text-gray-500">
                            {item.description}
                          </div>
                        )}
                      </div>
                      {item.requiresProfile && !hasProfile && (
                        <span className="text-xs text-amber-600">
                          Profile required
                        </span>
                      )}
                      <ChevronRight className="h-4 w-4 text-gray-400" />
                    </Command.Item>
                  );
                })}
              </Command.Group>
            ))}
          </Command.List>

          <div className="border-t border-gray-200 px-4 py-3">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1">
                  <kbd className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">↑↓</kbd>
                  Navigate
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">↵</kbd>
                  Select
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">esc</kbd>
                  Close
                </span>
              </div>
              <span className="text-gray-400">
                Press <kbd className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs">?</kbd> for shortcuts
              </span>
            </div>
          </div>
        </div>
      </div>
    </Command.Dialog>
  );
}