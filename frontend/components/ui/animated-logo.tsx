"use client"

import { motion, useReducedMotion } from "framer-motion"

import { cn } from "@/lib/utils"

interface AnimatedLogoProps {
  className?: string
  size?: "sm" | "default" | "lg" | "xl"
  animationType?: "continuous" | "once" | "hover" | "loading"
  duration?: number
}

export function AnimatedLogo({ 
  className,
  size = "default",
  animationType = "once",
  duration = 2
}: AnimatedLogoProps) {
  const shouldReduceMotion = useReducedMotion()
  
  const sizes = {
    sm: "h-16 w-16",
    default: "h-24 w-24",
    lg: "h-32 w-32",
    xl: "h-48 w-48"
  }

  // Animation variants
  const spinVariants = {
    initial: { 
      rotate: 0,
      scale: 0.8,
      opacity: 0 
    },
    animate: {
      rotate: shouldReduceMotion ? 0 : 360,
      scale: 1,
      opacity: 1,
      transition: {
        rotate: {
          duration,
          ease: "easeInOut"
        },
        scale: {
          duration: 0.5,
          ease: "easeOut"
        },
        opacity: {
          duration: 0.3
        }
      }
    },
    continuous: {
      rotate: 360,
      transition: {
        rotate: {
          duration,
          ease: "linear",
          repeat: Infinity
        }
      }
    },
    hover: {
      rotate: 360,
      transition: {
        duration: 0.6,
        ease: "easeInOut"
      }
    }
  }

  // Determine animation behavior
  const getAnimationProps = () => {
    switch (animationType) {
      case "continuous":
        return {
          initial: "initial",
          animate: ["animate", "continuous"],
          whileHover: { scale: 1.05 }
        }
      case "hover":
        return {
          initial: { rotate: 0 },
          whileHover: "hover",
          whileTap: { scale: 0.95 }
        }
      case "loading":
        return {
          animate: { rotate: 360 },
          transition: {
            duration: 1.5,
            ease: "linear",
            repeat: Infinity
          }
        }
      default: // "once"
        return {
          initial: "initial",
          animate: "animate",
          whileHover: { scale: 1.05 }
        }
    }
  }

  return (
    <motion.div
      className={cn(sizes[size], "relative", className)}
      variants={spinVariants}
      {...getAnimationProps()}
    >
      {/* Hexagon Container */}
      <svg
        viewBox="0 0 200 200"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Hexagon Background */}
        <path
          d="M100 10 L170 50 L170 130 L100 170 L30 130 L30 50 Z"
          className="fill-primary stroke-none"
        />
        
        {/* Gold Border (subtle) */}
        <path
          d="M100 10 L170 50 L170 130 L100 170 L30 130 L30 50 Z"
          className="fill-none stroke-gold/20 stroke-2"
        />
        
        {/* Asterisk/Star */}
        <g className="fill-white">
          {/* Vertical bar */}
          <rect x="90" y="40" width="20" height="120" rx="3" />
          
          {/* Diagonal bars */}
          <rect
            x="90" y="40" width="20" height="120" rx="3"
            transform="rotate(60 100 100)"
          />
          <rect
            x="90" y="40" width="20" height="120" rx="3"
            transform="rotate(-60 100 100)"
          />
        </g>
        
        {/* Gold accent on asterisk */}
        <g className="fill-none stroke-gold stroke-[3]">
          <rect x="90" y="40" width="20" height="120" rx="3" />
          <rect
            x="90" y="40" width="20" height="120" rx="3"
            transform="rotate(60 100 100)"
          />
          <rect
            x="90" y="40" width="20" height="120" rx="3"
            transform="rotate(-60 100 100)"
          />
        </g>
      </svg>

      {/* Optional glow effect */}
      <motion.div
        className="absolute inset-0 rounded-full bg-gold/10 blur-2xl"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ 
          opacity: [0, 0.3, 0],
          scale: [0.8, 1.2, 0.8] 
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </motion.div>
  )
}

// Hero Section Component with Animated Logo
export function HeroWithSpinningLogo() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-primary/5" />
      
      {/* Animated Logo */}
      <motion.div
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative z-10 text-center"
      >
        <AnimatedLogo 
          size="xl" 
          animationType="once"
          className="mx-auto mb-8"
        />
        
        <motion.h1
          className="text-5xl md:text-7xl font-bold mb-4"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.6 }}
        >
          rule<span className="text-gold">IQ</span>
        </motion.h1>
        
        <motion.p
          className="text-xl md:text-2xl text-muted-foreground"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.6 }}
        >
          AI Compliance Automated
        </motion.p>
      </motion.div>
    </section>
  )
}
