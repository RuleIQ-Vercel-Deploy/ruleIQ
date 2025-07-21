// Landing Page Hero Section with Spinning Logo
// Usage in app/page.tsx

import { motion, useScroll, useTransform } from 'framer-motion';
import { ArrowRight, Shield, Sparkles } from 'lucide-react';
import Link from 'next/link';

import { AnimatedLogo } from '@/components/ui/animated-logo';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function LandingHero() {
  const { scrollY } = useScroll();
  const logoRotate = useTransform(scrollY, [0, 300], [0, 180]);
  const logoScale = useTransform(scrollY, [0, 300], [1, 0.8]);

  return (
    <section className="relative flex min-h-screen items-center justify-center">
      {/* Animated background beams (CSS alternative to BeamsBackground) */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-gold/5" />
        <motion.div
          className="bg-gradient-conic absolute -right-1/2 -top-1/2 h-full w-full from-gold/10 via-transparent to-transparent"
          animate={{ rotate: 360 }}
          transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
        />
      </div>

      <div className="relative z-10 mx-auto max-w-4xl px-6 text-center">
        {/* Main animated logo */}
        <motion.div style={{ rotate: logoRotate, scale: logoScale }} className="mb-8">
          <AnimatedLogo size="xl" animationType="once" duration={2.5} className="mx-auto" />
        </motion.div>

        {/* Title with staggered animation */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
          <h1 className="mb-6 text-5xl font-bold md:text-7xl">
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
            className="mb-12 text-xl text-muted-foreground md:text-2xl"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 1.2, duration: 0.6 }}
          >
            AI Compliance Automated
          </motion.p>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          className="flex flex-col justify-center gap-4 sm:flex-row"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.6 }}
        >
          <Button size="lg" className="group gap-2">
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
          className="mt-12 flex items-center justify-center gap-2 text-sm text-muted-foreground"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2, duration: 0.6 }}
        >
          <Sparkles className="h-4 w-4 text-gold" />
          Trusted by 500+ UK SMBs
        </motion.p>
      </div>
    </section>
  );
}

// Loading State with Continuous Spin
export function LoadingLogo() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="text-center">
        <AnimatedLogo size="default" animationType="loading" className="mx-auto mb-4" />
        <p className="animate-pulse text-muted-foreground">Initializing compliance engine...</p>
      </div>
    </div>
  );
}

// Navigation Logo with Hover Spin
export function NavLogo() {
  return (
    <Link href="/" className="group flex items-center gap-3">
      <AnimatedLogo
        size="sm"
        animationType="hover"
        className="transition-transform group-hover:scale-105"
      />
      <span className="hidden text-xl font-bold sm:inline-block">
        rule<span className="text-gold">IQ</span>
      </span>
    </Link>
  );
}

// Feature Card with Subtle Animation
export function FeatureCardWithLogo({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <Card className="group transition-colors hover:border-gold/50">
      <CardHeader>
        <AnimatedLogo
          size="sm"
          animationType="hover"
          className="mb-4 opacity-10 transition-opacity group-hover:opacity-20"
        />
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
