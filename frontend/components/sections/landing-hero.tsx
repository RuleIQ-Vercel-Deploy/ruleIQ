// Landing Page Hero Section with Spinning Logo
// Usage in app/page.tsx

import Link from "next/link"
import { AnimatedLogo } from "@/components/ui/animated-logo"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, Shield, Sparkles } from "lucide-react"
import { motion, useScroll, useTransform } from "framer-motion"

export function LandingHero() {
  const { scrollY } = useScroll()
  const logoRotate = useTransform(scrollY, [0, 300], [0, 180])
  const logoScale = useTransform(scrollY, [0, 300], [1, 0.8])
  
  return (
    <section className="relative min-h-screen flex items-center justify-center">
      {/* Animated background beams (CSS alternative to BeamsBackground) */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-gold/5" />
        <motion.div
          className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-conic from-gold/10 via-transparent to-transparent"
          animate={{ rotate: 360 }}
          transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        />
      </div>

      <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
        {/* Main animated logo */}
        <motion.div
          style={{ rotate: logoRotate, scale: logoScale }}
          className="mb-8"
        >
          <AnimatedLogo 
            size="xl" 
            animationType="once"
            duration={2.5}
            className="mx-auto"
          />
        </motion.div>

        {/* Title with staggered animation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <motion.span
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.5 }}
            >
              rule
            </motion.span>
            <motion.span
              className="text-gold"
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 1, duration: 0.5 }}
            >
              IQ
            </motion.span>
          </h1>
          
          <motion.p
            className="text-xl md:text-2xl text-muted-foreground mb-12"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 1.2, duration: 0.6 }}
          >
            AI Compliance Automated
          </motion.p>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          className="flex flex-col sm:flex-row gap-4 justify-center"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.6 }}
        >
          <Button size="lg" className="gap-2 group">
            Get Started
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Button>
          <Button size="lg" variant="outline" className="gap-2">
            <Shield className="h-4 w-4" />
            See Demo
          </Button>
        </motion.div>

        {/* Trust indicator */}
        <motion.p
          className="mt-12 text-sm text-muted-foreground flex items-center justify-center gap-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2, duration: 0.6 }}
        >
          <Sparkles className="h-4 w-4 text-gold" />
          Trusted by 500+ UK SMBs
        </motion.p>
      </div>
    </section>
  )
}

// Loading State with Continuous Spin
export function LoadingLogo() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-50">
      <div className="text-center">
        <AnimatedLogo 
          size="default" 
          animationType="loading"
          className="mx-auto mb-4"
        />
        <p className="text-muted-foreground animate-pulse">
          Initializing compliance engine...
        </p>
      </div>
    </div>
  )
}

// Navigation Logo with Hover Spin
export function NavLogo() {
  return (
    <Link href="/" className="flex items-center gap-3 group">
      <AnimatedLogo 
        size="sm" 
        animationType="hover"
        className="transition-transform group-hover:scale-105"
      />
      <span className="font-bold text-xl hidden sm:inline-block">
        rule<span className="text-gold">IQ</span>
      </span>
    </Link>
  )
}

// Feature Card with Subtle Animation
export function FeatureCardWithLogo({ 
  title, 
  description 
}: { 
  title: string
  description: string 
}) {
  return (
    <Card className="group hover:border-gold/50 transition-colors">
      <CardHeader>
        <AnimatedLogo 
          size="sm" 
          animationType="hover"
          className="mb-4 opacity-10 group-hover:opacity-20 transition-opacity"
        />
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}
