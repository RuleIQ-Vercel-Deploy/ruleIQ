"use client";
import React, { useState } from "react";
import { motion } from "motion/react";
import { AlignJustify } from "lucide-react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { RuleIQLogo } from "./ruleiq-logo";

const RuleIQHeader = () => {
  const router = useRouter();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered1, setIsHovered1] = useState(false);
  const [isHovered2, setIsHovered2] = useState(false);

  const handleMouseMove = (event: React.MouseEvent<HTMLButtonElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setMousePosition({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    });
  };

  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="relative w-[80%] top-0 z-50 bg-[#0D0E0F] bg-transparent backdrop-blur-md border mt-8 rounded-xl border-[#252627]"
    >
      <div className="container mx-auto px-4 h-24 flex items-center justify-between">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Link href="/" className="flex items-center transform -translate-x-14 -translate-y-2">
            <RuleIQLogo variant="cyan" size="lg" />
          </Link>
        </motion.div>

        {/* Navigation Menu - Removed for cleaner header */}

        <AlignJustify className="w-6 h-6 md:hidden" />

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="hidden md:flex items-center gap-4"
        >
          <motion.button
            className="group relative overflow-hidden border-[2px] border-[#5B698B] rounded-full bg-gradient-to-b from-black to-[rgb(65,64,64)] px-8 py-2 text-white backdrop-blur-sm transition-colors hover:bg-[rgba(0,0,0,0.30)]"
            onMouseMove={handleMouseMove}
            onHoverStart={() => setIsHovered1(true)}
            onHoverEnd={() => setIsHovered1(false)}
            onClick={() => router.push("/login")}
          >
            <span className="relative z-10">Log in</span>
            {isHovered1 && (
              <motion.div
                className="absolute inset-0 z-0"
                animate={{
                  background: [
                    `radial-gradient(40px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(255,255,255,0.15), transparent 50%)`,
                  ],
                }}
                transition={{ duration: 0.15 }}
              />
            )}
          </motion.button>

          <motion.button
            className="group relative flex border-[2px] border-[#5B698B] overflow-hidden rounded-full bg-gradient-to-b from-[rgb(91,105,139)] to-[#414040] px-8 py-2 text-white backdrop-blur-sm transition-colors hover:bg-[rgba(255,255,255,0.2)]"
            onMouseMove={handleMouseMove}
            onHoverStart={() => setIsHovered2(true)}
            onHoverEnd={() => setIsHovered2(false)}
            onClick={() => router.push("/register")}
          >
            <span className="relative z-10">Get Started</span>
            {isHovered2 && (
              <motion.div
                className="absolute inset-0 z-0"
                animate={{
                  background: [
                    `radial-gradient(40px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(255,255,255,0.2), transparent 50%)`,
                  ],
                }}
                transition={{ duration: 0.15 }}
              />
            )}
          </motion.button>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default RuleIQHeader;
