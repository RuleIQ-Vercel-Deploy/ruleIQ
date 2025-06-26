"use client";
import React from "react";
import Image from "next/image";

interface RuleIQLogoProps {
  className?: string;
  variant?: "cyan" | "navy" | "icon" | "hero";
  size?: "sm" | "md" | "lg" | "xl" | "2xl";
}

export const RuleIQLogo = ({
  className = "",
  variant = "navy",
  size = "md"
}: RuleIQLogoProps) => {
  const sizeClasses = {
    sm: "h-24",
    md: "h-48",
    lg: "h-72",
    xl: "h-96",
    "2xl": "h-[40rem]"
  };

  const logoSrc = variant === "icon"
    ? "/ruleiq-icon.png"
    : variant === "cyan"
      ? "/ruleiq-logo-cyan.png"
      : variant === "hero"
        ? "/ruleiq-hero-logo.png"
        : "/ruleiq-logo-navy.png";

  const altText = variant === "icon"
    ? "ruleIQ Icon"
    : "ruleIQ - AI-Driven Compliance Automation";

  return (
    <div className={`flex items-center ${className}`}>
      <Image
        src={logoSrc}
        alt={altText}
        width={variant === "icon" ? 800 : 4000}
        height={variant === "icon" ? 800 : 2000}
        className={`${sizeClasses[size]} w-auto logo-enhanced`}
        priority
      />
    </div>
  );
};
