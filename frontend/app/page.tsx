"use client";

import { motion, useScroll, useTransform } from "framer-motion";
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
  ChevronRight
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useState, useEffect, useRef } from "react";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/stores/auth.store";
import { cn } from "@/lib/utils";

// Hero Section with Animated Background
const HeroSection = () => {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  });
  
  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const opacity = useTransform(scrollYProgress, [0, 1], [1, 0]);

  return (
    <section ref={containerRef} className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated Mesh Gradient Background */}
      <motion.div 
        className="absolute inset-0 mesh-gradient"
        style={{ y }}
      />
      
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
            ease: "linear"
          }}
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-primary/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-brand-secondary/20 rounded-full blur-3xl"
        />
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]" />

      {/* Content */}
      <motion.div 
        className="relative z-10 container mx-auto px-4 text-center"
        style={{ opacity }}
      >
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-8"
        >
          <Sparkles className="w-4 h-4 text-brand-secondary" />
          <span className="text-sm font-medium text-text-primary">
            AI-Powered Compliance Automation
          </span>
        </motion.div>

        {/* Main Heading */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-6xl md:text-8xl font-bold mb-6"
        >
          <span className="gradient-text">Transform</span>
          <br />
          <span className="text-text-primary">Your Compliance</span>
        </motion.h1>

        {/* Subheading */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-xl md:text-2xl text-text-secondary max-w-3xl mx-auto mb-12"
        >
          Automate compliance management with AI. Cut costs by 60%, reduce audit prep by 75%, 
          and achieve 99.9% accuracy across 50+ frameworks.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12"
        >
          <Button
            size="lg"
            className="btn-gradient group px-8 py-6 text-lg"
            onClick={() => router.push(isAuthenticated ? "/dashboard" : "/signup")}
          >
            {isAuthenticated ? "Go to Dashboard" : "Start Free Trial"}
            <ArrowRight className="ml-2 w-5 h-5 transition-transform group-hover:translate-x-1" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="glass-card border-glass-border hover:bg-glass-white-hover px-8 py-6 text-lg"
            onClick={() => router.push("/demo")}
          >
            Watch Demo
            <ChevronRight className="ml-2 w-5 h-5" />
          </Button>
        </motion.div>

        {/* Trust Indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex flex-wrap gap-8 justify-center items-center"
        >
          <div className="flex items-center gap-2 text-text-secondary">
            <Shield className="w-5 h-5 text-brand-tertiary" />
            <span className="text-sm">SOC 2 Certified</span>
          </div>
          <div className="flex items-center gap-2 text-text-secondary">
            <Lock className="w-5 h-5 text-brand-tertiary" />
            <span className="text-sm">Bank-Grade Security</span>
          </div>
          <div className="flex items-center gap-2 text-text-secondary">
            <Globe className="w-5 h-5 text-brand-tertiary" />
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
          className="w-6 h-10 rounded-full border-2 border-text-secondary/30 flex items-start justify-center p-2"
        >
          <motion.div className="w-1 h-2 bg-text-secondary/50 rounded-full" />
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
      className="glass-card p-8 hover:border-brand-primary/50 transition-all duration-300 group"
    >
      <div className="mb-4 p-3 rounded-lg bg-brand-primary/10 w-fit group-hover:bg-brand-primary/20 transition-colors">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-text-primary mb-3">{title}</h3>
      <p className="text-text-secondary">{description}</p>
    </motion.div>
  );
};

// Stats Section with Animated Numbers
const StatsSection = () => {
  const stats = [
    { value: "60%", label: "Cost Reduction", suffix: "" },
    { value: "75%", label: "Faster Audits", suffix: "" },
    { value: "99.9%", label: "Accuracy Rate", suffix: "" },
    { value: "50", label: "Frameworks", suffix: "+" },
  ];

  return (
    <section className="py-24 relative">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="text-5xl md:text-6xl font-bold gradient-text mb-2">
                {stat.value}{stat.suffix}
              </div>
              <div className="text-text-secondary">{stat.label}</div>
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
    <div className="glass-card p-8 h-full">
      <div className="flex gap-1 mb-4">
        {[...Array(rating)].map((_, i) => (
          <Star key={i} className="w-5 h-5 fill-brand-secondary text-brand-secondary" />
        ))}
      </div>
      <p className="text-text-primary mb-6 text-lg italic">&ldquo;{quote}&rdquo;</p>
      <div className="mt-auto">
        <p className="font-semibold text-text-primary">{author}</p>
        <p className="text-sm text-brand-secondary">{role}</p>
        <p className="text-sm text-text-secondary">{company}</p>
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

const PricingCard = ({ name, price, description, features, popular = false, onSelect }: PricingCardProps) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300 }}
      className={cn(
        "relative glass-card p-8",
        popular && "border-brand-primary glow-purple"
      )}
    >
      {popular && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
          <span className="px-4 py-1 rounded-full bg-gradient-to-r from-brand-primary to-brand-secondary text-white text-sm font-medium">
            Most Popular
          </span>
        </div>
      )}
      
      <div className="text-center mb-8">
        <h3 className="text-2xl font-bold text-text-primary mb-2">{name}</h3>
        <div className="text-4xl font-bold gradient-text mb-2">{price}</div>
        <p className="text-text-secondary">{description}</p>
      </div>

      <ul className="space-y-3 mb-8">
        {features.map((feature, i) => (
          <li key={i} className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-brand-tertiary flex-shrink-0 mt-0.5" />
            <span className="text-text-secondary text-sm">{feature}</span>
          </li>
        ))}
      </ul>

      <Button
        className={cn(
          "w-full",
          popular ? "btn-gradient" : "glass-card hover:bg-glass-white-hover"
        )}
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
      <div className="min-h-screen bg-surface-base flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-brand-primary border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-base">
      {/* Navigation */}
      <header className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-glass-border">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold gradient-text">
            ruleIQ
          </Link>
          
          <nav className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-text-secondary hover:text-text-primary transition-colors">
              Features
            </Link>
            <Link href="#pricing" className="text-text-secondary hover:text-text-primary transition-colors">
              Pricing
            </Link>
            <Link href="#testimonials" className="text-text-secondary hover:text-text-primary transition-colors">
              Testimonials
            </Link>
          </nav>

          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              className="text-text-secondary hover:text-text-primary"
              onClick={() => router.push("/login")}
            >
              Sign In
            </Button>
            <Button
              className="btn-gradient"
              onClick={() => router.push("/signup")}
            >
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
      <section id="features" className="py-24 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="gradient-text">Powerful Features</span>
            </h2>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto">
              Everything you need to automate compliance and reduce risk
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Zap className="w-8 h-8 text-brand-secondary" />}
              title="AI-Powered Analysis"
              description="Intelligent gap analysis and automated evidence collection powered by advanced AI"
              delay={0}
            />
            <FeatureCard
              icon={<Shield className="w-8 h-8 text-brand-secondary" />}
              title="Real-Time Monitoring"
              description="Continuous compliance tracking with instant alerts for any deviations"
              delay={0.1}
            />
            <FeatureCard
              icon={<BarChart3 className="w-8 h-8 text-brand-secondary" />}
              title="Smart Reporting"
              description="Generate comprehensive compliance reports with a single click"
              delay={0.2}
            />
            <FeatureCard
              icon={<Users className="w-8 h-8 text-brand-secondary" />}
              title="Team Collaboration"
              description="Streamline workflows and enable seamless team coordination"
              delay={0.3}
            />
            <FeatureCard
              icon={<FileCheck className="w-8 h-8 text-brand-secondary" />}
              title="Policy Automation"
              description="Auto-generate and maintain policies aligned with your frameworks"
              delay={0.4}
            />
            <FeatureCard
              icon={<TrendingUp className="w-8 h-8 text-brand-secondary" />}
              title="Risk Assessment"
              description="Proactive risk identification and mitigation recommendations"
              delay={0.5}
            />
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-24 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="gradient-text">Loved by Teams</span>
            </h2>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto">
              See what compliance professionals are saying about ruleIQ
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
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
      <section id="pricing" className="py-24 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="gradient-text">Simple Pricing</span>
            </h2>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto">
              Choose the plan that fits your compliance needs
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <PricingCard
              name="Starter"
              price="£149/mo"
              description="Perfect for small teams"
              features={[
                "Up to 2 frameworks",
                "Basic AI analysis",
                "Monthly reports",
                "Email support",
                "1 user account"
              ]}
              onSelect={() => router.push("/signup?plan=starter")}
            />
            <PricingCard
              name="Professional"
              price="£499/mo"
              description="For growing companies"
              features={[
                "Unlimited frameworks",
                "Advanced AI features",
                "Real-time monitoring",
                "Priority support",
                "5 user accounts",
                "Custom policies",
                "API access"
              ]}
              popular
              onSelect={() => router.push("/signup?plan=professional")}
            />
            <PricingCard
              name="Enterprise"
              price="Custom"
              description="For large organizations"
              features={[
                "Everything in Pro",
                "Unlimited users",
                "Dedicated support",
                "Custom integrations",
                "SLA guarantees",
                "On-premise option",
                "White-label"
              ]}
              onSelect={() => router.push("/contact-sales")}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="gradient-bg rounded-3xl p-16 text-center"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Ready to Transform Your Compliance?
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              Join thousands of companies automating their compliance with AI
            </p>
            <Button
              size="lg"
              className="bg-white text-brand-primary hover:bg-neutral-100 px-8 py-6 text-lg font-semibold"
              onClick={() => router.push("/signup")}
            >
              Start Your Free Trial
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 border-t border-glass-border">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="text-2xl font-bold gradient-text mb-4">ruleIQ</h3>
              <p className="text-text-secondary">
                AI-powered compliance automation for modern businesses
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-text-primary mb-4">Product</h4>
              <ul className="space-y-2 text-text-secondary">
                <li><Link href="/features" className="hover:text-text-primary transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-text-primary transition-colors">Pricing</Link></li>
                <li><Link href="/integrations" className="hover:text-text-primary transition-colors">Integrations</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-text-primary mb-4">Company</h4>
              <ul className="space-y-2 text-text-secondary">
                <li><Link href="/about" className="hover:text-text-primary transition-colors">About</Link></li>
                <li><Link href="/blog" className="hover:text-text-primary transition-colors">Blog</Link></li>
                <li><Link href="/careers" className="hover:text-text-primary transition-colors">Careers</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-text-primary mb-4">Support</h4>
              <ul className="space-y-2 text-text-secondary">
                <li><Link href="/help" className="hover:text-text-primary transition-colors">Help Center</Link></li>
                <li><Link href="/contact" className="hover:text-text-primary transition-colors">Contact</Link></li>
                <li><Link href="/status" className="hover:text-text-primary transition-colors">Status</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-glass-border pt-8 text-center text-text-secondary">
            <p>&copy; 2025 ruleIQ. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}