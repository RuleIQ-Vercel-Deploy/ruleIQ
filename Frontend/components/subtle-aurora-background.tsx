"use client";
import { cn } from "@/lib/utils";
import React, { ReactNode } from "react";

interface SubtleAuroraBackgroundProps extends React.HTMLProps<HTMLDivElement> {
  children: ReactNode;
  showRadialGradient?: boolean;
}

export const SubtleAuroraBackground = ({
  className,
  children,
  showRadialGradient = true,
  ...props
}: SubtleAuroraBackgroundProps) => {
  return (
    <main>
      <div
        className={cn(
          "transition-bg relative flex h-[100vh] flex-col items-center justify-center bg-zinc-950 text-white",
          className,
        )}
        {...props}
      >
        <div
          className="absolute inset-0 overflow-hidden"
          style={
            {
              // Much more subtle color palette - grays and muted blues
              "--subtle-aurora":
                "repeating-linear-gradient(100deg,#1f2937_10%,#374151_15%,#4b5563_20%,#6b7280_25%,#1f2937_30%)",
              "--dark-gradient":
                "repeating-linear-gradient(100deg,#000_0%,#000_7%,transparent_10%,transparent_12%,#000_16%)",
              "--white-gradient":
                "repeating-linear-gradient(100deg,#111827_0%,#111827_7%,transparent_10%,transparent_12%,#111827_16%)",
              
              // Muted color variables
              "--gray-800": "#1f2937",
              "--gray-700": "#374151", 
              "--gray-600": "#4b5563",
              "--gray-500": "#6b7280",
              "--gray-900": "#111827",
              "--black": "#000",
              "--transparent": "transparent",
            } as React.CSSProperties
          }
        >
          <div
            className={cn(
              `after:animate-aurora pointer-events-none absolute -inset-[10px] [background-image:var(--white-gradient),var(--subtle-aurora)] [background-size:400%,_300%] [background-position:50%_50%,50%_50%] opacity-20 blur-[20px] filter will-change-transform [--subtle-aurora:repeating-linear-gradient(100deg,var(--gray-800)_10%,var(--gray-700)_15%,var(--gray-600)_20%,var(--gray-500)_25%,var(--gray-800)_30%)] [--dark-gradient:repeating-linear-gradient(100deg,var(--black)_0%,var(--black)_7%,var(--transparent)_10%,var(--transparent)_12%,var(--black)_16%)] [--white-gradient:repeating-linear-gradient(100deg,var(--gray-900)_0%,var(--gray-900)_7%,var(--transparent)_10%,var(--transparent)_12%,var(--gray-900)_16%)] after:absolute after:inset-0 after:[background-image:var(--white-gradient),var(--subtle-aurora)] after:[background-size:300%,_200%] after:[background-attachment:fixed] after:mix-blend-soft-light after:content-[""] after:opacity-30`,

              showRadialGradient &&
                `[mask-image:radial-gradient(ellipse_at_50%_0%,black_20%,var(--transparent)_80%)]`,
            )}
          ></div>
        </div>
        {children}
      </div>
    </main>
  );
};
