'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import {
  ArrowRight,
  Sparkles,
  Shield,
  Zap,
  BarChart3,
  Lock,
  Globe,
  CheckCircle,
  Star,
  TrendingUp,
  Users,
  FileCheck,
  ChevronRight,
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import React, { useState, useEffect, useRef } from 'react';

import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/lib/stores/auth.store';
import { cn } from '@/lib/utils';

// Hero Section with Animated Background
const HeroSection = () => {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end start'],
  });

  const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%']);
  const opacity = useTransform(scrollYProgress, [0, 1], [1, 0]);

  return (
    <section
      ref={containerRef}
      className="relative flex min-h-screen items-center justify-center overflow-hidden"
    >
      {/* Animated Mesh Gradient Background */}
      <motion.div className="mesh-gradient absolute inset-0" style={{ y }} />

      {/* Floating Orbs */}
      <div className="absolute inset-0">
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -100, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute left-1/4 top-1/4 h-96 w-96 rounded-full bg-primary/20 blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-secondary/20 blur-3xl"
        />
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]" />

      {/* Content */}
      <motion.div className="container relative z-10 mx-auto px-4 text-center" style={{ opacity }}>
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="glass-card mb-8 inline-flex items-center gap-2 rounded-full px-4 py-2"
        >
          <Sparkles className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium text-foreground">
            AI-Powered Compliance Automation
          </span>
        </motion.div>

        {/* Main Heading */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-6 text-6xl font-bold md:text-8xl"
        >
          <span className="gradient-text">Transform</span>
          <br />
          <span className="text-foreground">Your Compliance</span>
        </motion.h1>

        {/* Subheading */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mx-auto mb-12 max-w-3xl text-xl text-muted-foreground md:text-2xl"
        >
          Automate compliance management with AI. Cut costs by 60%, reduce audit prep by 75%, and
          achieve 99.9% accuracy across 50+ frameworks.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mb-12 flex flex-col items-center justify-center gap-4 sm:flex-row"
        >
          <Button
            size="lg"
            className="btn-gradient group px-8 py-6 text-lg"
            onClick={() => router.push(isAuthenticated ? '/dashboard' : '/signup')}
          >
            {isAuthenticated ? 'Go to Dashboard' : 'Start Free Trial'}
            <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="glass-card border-glass-border px-8 py-6 text-lg hover:bg-glass-white-hover"
            onClick={() => router.push('/demo')}
          >
            Watch Demo
            <ChevronRight className="ml-2 h-5 w-5" />
          </Button>
        </motion.div>

        {/* Trust Indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex flex-wrap items-center justify-center gap-8"
        >
          <div className="flex items-center gap-2 text-muted-foreground">
            <Shield className="h-5 w-5 text-primary" />
            <span className="text-sm">SOC 2 Certified</span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Lock className="h-5 w-5 text-primary" />
            <span className="text-sm">Bank-Grade Security</span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Globe className="h-5 w-5 text-primary" />
            <span className="text-sm">GDPR Compliant</span>
          </div>
        </motion.div>
      </motion.div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="flex h-10 w-6 items-start justify-center rounded-full border-2 border-text-secondary/30 p-2"
        >
          <motion.div className="h-2 w-1 rounded-full bg-text-secondary/50" />
        </motion.div>
      </motion.div>
    </section>
  );
};

// Feature Card Component with Glass Effect
interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  delay?: number;
}

const FeatureCard = ({ icon, title, description, delay = 0 }: FeatureCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      viewport={{ once: true }}
      className="glass-card group p-8 transition-all duration-300 hover:border-brand-primary/50"
    >
      <div className="mb-4 w-fit rounded-lg bg-primary/10 p-3 transition-colors group-hover:bg-primary/20">
        {icon}
      </div>
      <h3 className="mb-3 text-xl font-semibold text-foreground">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </motion.div>
  );
};

// Stats Section with Animated Numbers
const StatsSection = () => {
  const stats = [
    { value: '60%', label: 'Cost Reduction', suffix: '' },
    { value: '75%', label: 'Faster Audits', suffix: '' },
    { value: '99.9%', label: 'Accuracy Rate', suffix: '' },
    { value: '50', label: 'Frameworks', suffix: '+' },
  ];

  return (
    <section className="relative py-24">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="gradient-text mb-2 text-5xl font-bold md:text-6xl">
                {stat.value}
                {stat.suffix}
              </div>
              <div className="text-muted-foreground">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Modern Testimonial Card
interface TestimonialProps {
  quote: string;
  author: string;
  role: string;
  company: string;
  rating: number;
}

const TestimonialCard = ({ quote, author, role, company, rating }: TestimonialProps) => {
  return (
    <div className="glass-card h-full p-8">
      <div className="mb-4 flex gap-1">
        {[...Array(rating)].map((_, i) => (
          <Star key={i} className="h-5 w-5 fill-primary text-primary" />
        ))}
      </div>
      <p className="mb-6 text-lg italic text-foreground">&ldquo;{quote}&rdquo;</p>
      <div className="mt-auto">
        <p className="font-semibold text-foreground">{author}</p>
        <p className="text-sm text-primary">{role}</p>
        <p className="text-sm text-muted-foreground">{company}</p>
      </div>
    </div>
  );
};

// Modern Pricing Card
interface PricingCardProps {
  name: string;
  price: string;
  description: string;
  features: string[];
  popular?: boolean;
  onSelect: () => void;
}

const PricingCard = ({
  name,
  price,
  description,
  features,
  popular = false,
  onSelect,
}: PricingCardProps) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ type: 'spring', stiffness: 300 }}
      className={cn('glass-card relative p-8', popular && 'glow-purple border-brand-primary')}
    >
      {popular && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
          <span className="rounded-full bg-gradient-to-r from-brand-primary to-brand-secondary px-4 py-1 text-sm font-medium text-white">
            Most Popular
          </span>
        </div>
      )}

      <div className="mb-8 text-center">
        <h3 className="mb-2 text-2xl font-bold text-foreground">{name}</h3>
        <div className="gradient-text mb-2 text-4xl font-bold">{price}</div>
        <p className="text-muted-foreground">{description}</p>
      </div>

      <ul className="mb-8 space-y-3">
        {features.map((feature, i) => (
          <li key={i} className="flex items-start gap-3">
            <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-primary" />
            <span className="text-sm text-muted-foreground">{feature}</span>
          </li>
        ))}
      </ul>

      <Button
        className={cn('w-full', popular ? 'btn-gradient' : 'glass-card hover:bg-glass-white-hover')}
        onClick={onSelect}
      >
        Get Started
      </Button>
    </motion.div>
  );
};

export default function HomePage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-surface-base">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="h-16 w-16 rounded-full border-4 border-brand-primary border-t-transparent"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-base">
      {/* Navigation */}
      <header className="glass-card fixed left-0 right-0 top-0 z-50 border-b border-glass-border">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="gradient-text text-2xl font-bold">
            ruleIQ
          </Link>

          <nav className="hidden items-center gap-8 md:flex">
            <Link
              href="#features"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Features
            </Link>
            <Link
              href="#pricing"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Pricing
            </Link>
            <Link
              href="#testimonials"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Testimonials
            </Link>
          </nav>

          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              className="text-muted-foreground hover:text-foreground"
              onClick={() => router.push('/login')}
            >
              Sign In
            </Button>
            <Button className="btn-gradient" onClick={() => router.push('/signup')}>
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <HeroSection />

      {/* Stats Section */}
      <StatsSection />

      {/* Features Section */}
      <section id="features" className="relative py-24">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="mb-16 text-center"
          >
            <h2 className="mb-4 text-4xl font-bold md:text-5xl">
              <span className="gradient-text">Powerful Features</span>
            </h2>
            <p className="mx-auto max-w-3xl text-xl text-muted-foreground">
              Everything you need to automate compliance and reduce risk
            </p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              icon={<Zap className="h-8 w-8 text-primary" />}
              title="AI-Powered Analysis"
              description="Intelligent gap analysis and automated evidence collection powered by advanced AI"
              delay={0}
            />
            <FeatureCard
              icon={<Shield className="h-8 w-8 text-primary" />}
              title="Real-Time Monitoring"
              description="Continuous compliance tracking with instant alerts for any deviations"
              delay={0.1}
            />
            <FeatureCard
              icon={<BarChart3 className="h-8 w-8 text-primary" />}
              title="Smart Reporting"
              description="Generate comprehensive compliance reports with a single click"
              delay={0.2}
            />
            <FeatureCard
              icon={<Users className="h-8 w-8 text-primary" />}
              title="Team Collaboration"
              description="Streamline workflows and enable seamless team coordination"
              delay={0.3}
            />
            <FeatureCard
              icon={<FileCheck className="h-8 w-8 text-primary" />}
              title="Policy Automation"
              description="Auto-generate and maintain policies aligned with your frameworks"
              delay={0.4}
            />
            <FeatureCard
              icon={<TrendingUp className="h-8 w-8 text-primary" />}
              title="Risk Assessment"
              description="Proactive risk identification and mitigation recommendations"
              delay={0.5}
            />
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="relative py-24">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="mb-16 text-center"
          >
            <h2 className="mb-4 text-4xl font-bold md:text-5xl">
              <span className="gradient-text">Loved by Teams</span>
            </h2>
            <p className="mx-auto max-w-3xl text-xl text-muted-foreground">
              See what compliance professionals are saying about ruleIQ
            </p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-3">
            <TestimonialCard
              quote="ruleIQ transformed our compliance process. What used to take weeks now takes days."
              author="Sarah Chen"
              role="CISO"
              company="TechFlow Solutions"
              rating={5}
            />
            <TestimonialCard
              quote="The AI recommendations are spot-on. It's like having a compliance expert on call 24/7."
              author="Michael Rodriguez"
              role="Compliance Officer"
              company="HealthCare Plus"
              rating={5}
            />
            <TestimonialCard
              quote="We saved over $200K in compliance costs within the first year. Incredible ROI."
              author="Jennifer Walsh"
              role="VP Risk Management"
              company="Global Finance Corp"
              rating={5}
            />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="relative py-24">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="mb-16 text-center"
          >
            <h2 className="mb-4 text-4xl font-bold md:text-5xl">
              <span className="gradient-text">Simple Pricing</span>
            </h2>
            <p className="mx-auto max-w-3xl text-xl text-muted-foreground">
              Choose the plan that fits your compliance needs
            </p>
          </motion.div>

          <div className="mx-auto grid max-w-6xl gap-8 md:grid-cols-3">
            <PricingCard
              name="Starter"
              price="£149/mo"
              description="Perfect for small teams"
              features={[
                'Up to 2 frameworks',
                'Basic AI analysis',
                'Monthly reports',
                'Email support',
                '1 user account',
              ]}
              onSelect={() => router.push('/signup?plan=starter')}
            />
            <PricingCard
              name="Professional"
              price="£499/mo"
              description="For growing companies"
              features={[
                'Unlimited frameworks',
                'Advanced AI features',
                'Real-time monitoring',
                'Priority support',
                '5 user accounts',
                'Custom policies',
                'API access',
              ]}
              popular
              onSelect={() => router.push('/signup?plan=professional')}
            />
            <PricingCard
              name="Enterprise"
              price="Custom"
              description="For large organizations"
              features={[
                'Everything in Pro',
                'Unlimited users',
                'Dedicated support',
                'Custom integrations',
                'SLA guarantees',
                'On-premise option',
                'White-label',
              ]}
              onSelect={() => router.push('/contact-sales')}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-24">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="gradient-bg rounded-3xl p-16 text-center"
          >
            <h2 className="mb-4 text-4xl font-bold text-white md:text-5xl">
              Ready to Transform Your Compliance?
            </h2>
            <p className="mx-auto mb-8 max-w-2xl text-xl text-white/90">
              Join thousands of companies automating their compliance with AI
            </p>
            <Button
              size="lg"
              className="bg-white px-8 py-6 text-lg font-semibold text-primary hover:bg-neutral-100"
              onClick={() => router.push('/signup')}
            >
              Start Your Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-glass-border py-16">
        <div className="container mx-auto px-4">
          <div className="mb-8 grid gap-8 md:grid-cols-4">
            <div>
              <h3 className="gradient-text mb-4 text-2xl font-bold">ruleIQ</h3>
              <p className="text-muted-foreground">
                AI-powered compliance automation for modern businesses
              </p>
            </div>

            <div>
              <h4 className="mb-4 font-semibold text-foreground">Product</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <Link href="/features" className="transition-colors hover:text-foreground">
                    Features
                  </Link>
                </li>
                <li>
                  <Link href="/pricing" className="transition-colors hover:text-foreground">
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link href="/integrations" className="transition-colors hover:text-foreground">
                    Integrations
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="mb-4 font-semibold text-foreground">Company</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <Link href="/about" className="transition-colors hover:text-foreground">
                    About
                  </Link>
                </li>
                <li>
                  <Link href="/blog" className="transition-colors hover:text-foreground">
                    Blog
                  </Link>
                </li>
                <li>
                  <Link href="/careers" className="transition-colors hover:text-foreground">
                    Careers
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="mb-4 font-semibold text-foreground">Support</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>
                  <Link href="/help" className="transition-colors hover:text-foreground">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="transition-colors hover:text-foreground">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link href="/status" className="transition-colors hover:text-foreground">
                    Status
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-glass-border pt-8 text-center text-muted-foreground">
            <p>&copy; 2025 ruleIQ. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
