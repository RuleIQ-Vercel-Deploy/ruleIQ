'use client';

import React from 'react';
import { Check, X, MoveRight, Sparkles, Shield, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { cn } from '@/lib/utils';

const pricingPlans = [
  {
    name: "Starter",
    description: "Perfect for small businesses getting started with compliance automation",
    price: "£99",
    period: "month",
    badge: null,
    features: [
      { name: "Core Compliance Engine", included: true },
      { name: "Up to 10 policies", included: true },
      { name: "Basic risk assessment", included: true },
      { name: "Email support", included: true },
      { name: "Regulatory updates", included: true },
      { name: "AI-powered analysis", included: false },
      { name: "Custom workflows", included: false },
      { name: "API access", included: false },
    ],
    cta: {
      text: "Start Free Trial",
      variant: "secondary",
      href: "/auth/sign-up?plan=starter"
    }
  },
  {
    name: "Professional",
    description: "Advanced features for growing organizations with complex compliance needs",
    price: "£299",
    period: "month",
    badge: "MOST POPULAR",
    features: [
      { name: "Everything in Starter", included: true },
      { name: "Unlimited policies", included: true },
      { name: "AI-powered analysis", included: true },
      { name: "Custom workflows", included: true },
      { name: "Priority support", included: true },
      { name: "Advanced reporting", included: true },
      { name: "API access", included: true },
      { name: "White-label options", included: false },
    ],
    cta: {
      text: "Start Free Trial",
      variant: "primary",
      href: "/auth/sign-up?plan=professional"
    }
  },
  {
    name: "Enterprise",
    description: "Tailored solutions for large organizations with enterprise requirements",
    price: "Custom",
    period: null,
    badge: null,
    features: [
      { name: "Everything in Professional", included: true },
      { name: "Unlimited everything", included: true },
      { name: "Dedicated account manager", included: true },
      { name: "Custom integrations", included: true },
      { name: "White-label options", included: true },
      { name: "On-premise deployment", included: true },
      { name: "SLA guarantee", included: true },
      { name: "24/7 phone support", included: true },
    ],
    cta: {
      text: "Contact Sales",
      variant: "secondary",
      href: "/contact-sales"
    }
  }
];

interface PricingCardProps {
  plan: typeof pricingPlans[0];
  index: number;
  isPopular: boolean;
}

function PricingCard({ plan, index, isPopular }: PricingCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className={cn(
        "relative group",
        isPopular && "lg:-mt-4"
      )}
    >
      {/* Glow effect for popular plan */}
      {isPopular && (
        <div className="absolute -inset-0.5 bg-gradient-to-r from-neural-purple-600 to-neural-purple-400 
                        rounded-3xl opacity-20 blur-xl" />
      )}
      
      <div className={cn(
        "relative bg-black/50 border rounded-3xl p-8 h-full backdrop-blur-sm transition-all duration-300",
        isPopular 
          ? "border-neural-purple-500/30 hover:border-neural-purple-500/50" 
          : "border-neural-purple-500/10 hover:border-neural-purple-500/30",
        "hover:-translate-y-1"
      )}>
        {/* Badge */}
        {plan.badge && (
          <div className="absolute -top-4 left-1/2 -translate-x-1/2">
            <div className="bg-gradient-to-r from-neural-purple-500 to-neural-purple-600 
                            text-white text-xs font-light tracking-wider 
                            px-4 py-1.5 rounded-full">
              {plan.badge}
            </div>
          </div>
        )}
        
        {/* Plan name and description */}
        <div className="mb-8">
          <h3 className="text-2xl font-light text-white mb-3">
            {plan.name}
          </h3>
          <p className="text-sm font-light text-white/60 leading-relaxed">
            {plan.description}
          </p>
        </div>
        
        {/* Pricing */}
        <div className="mb-8">
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extralight text-white">
              {plan.price}
            </span>
            {plan.period && (
              <span className="text-sm font-light text-white/40">
                / {plan.period}
              </span>
            )}
          </div>
        </div>
        
        {/* Features */}
        <ul className="space-y-4 mb-8">
          {plan.features.map((feature, idx) => (
            <li key={idx} className="flex items-center gap-3">
              {feature.included ? (
                <Check className="w-4 h-4 text-neural-purple-400 flex-shrink-0" />
              ) : (
                <X className="w-4 h-4 text-white/20 flex-shrink-0" />
              )}
              <span className={cn(
                "text-sm font-light",
                feature.included ? "text-white/75" : "text-white/30"
              )}>
                {feature.name}
              </span>
            </li>
          ))}
        </ul>
        
        {/* CTA */}
        <Link
          href={plan.cta.href}
          className={cn(
            "w-full inline-flex items-center justify-center gap-2",
            "px-6 py-3 rounded-2xl font-light tracking-tight",
            "transition-all duration-300",
            plan.cta.variant === 'primary' 
              ? "bg-gradient-to-r from-neural-purple-500 to-neural-purple-600 text-white border border-neural-purple-500/20 hover:from-neural-purple-400 hover:to-neural-purple-500 hover:-translate-y-0.5 hover:shadow-purple-md"
              : "bg-transparent text-white border border-white/10 hover:bg-white/5 hover:border-white/20"
          )}
        >
          {plan.cta.text}
          <MoveRight className="w-4 h-4" />
        </Link>
      </div>
    </motion.div>
  );
}

export default function PricingPreview() {
  return (
    <section id="pricing" className="relative py-24 px-6 bg-gradient-to-b from-black to-neural-purple-900/10">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 bg-neural-purple-500/10 
                       text-neural-purple-400 text-xs font-light tracking-wider 
                       uppercase px-3 py-1 rounded-full border border-neural-purple-500/20 mb-6"
          >
            <Sparkles className="w-3 h-3" />
            PRICING
          </motion.div>
          
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl font-extralight tracking-tight text-white mb-6"
          >
            Simple, Transparent Pricing
          </motion.h2>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg font-light text-white/60 max-w-3xl mx-auto"
          >
            Choose the perfect plan for your compliance needs. All plans include a 14-day free trial.
          </motion.p>
        </div>
        
        {/* Pricing Cards */}
        <div className="grid lg:grid-cols-3 gap-8 lg:gap-6">
          {pricingPlans.map((plan, index) => (
            <PricingCard
              key={plan.name}
              plan={plan}
              index={index}
              isPopular={plan.badge === "MOST POPULAR"}
            />
          ))}
        </div>
        
        {/* Bottom Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-16 grid sm:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl 
                            bg-neural-purple-500/10 mb-4">
              <Shield className="w-6 h-6 text-neural-purple-400" />
            </div>
            <h4 className="text-lg font-light text-white mb-2">
              No Hidden Fees
            </h4>
            <p className="text-sm font-light text-white/60">
              What you see is what you pay. No surprises.
            </p>
          </div>
          
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl 
                            bg-neural-purple-500/10 mb-4">
              <Zap className="w-6 h-6 text-neural-purple-400" />
            </div>
            <h4 className="text-lg font-light text-white mb-2">
              Cancel Anytime
            </h4>
            <p className="text-sm font-light text-white/60">
              No long-term contracts. Cancel whenever you want.
            </p>
          </div>
          
          <div className="text-center sm:col-span-2 lg:col-span-1">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl 
                            bg-neural-purple-500/10 mb-4">
              <Sparkles className="w-6 h-6 text-neural-purple-400" />
            </div>
            <h4 className="text-lg font-light text-white mb-2">
              Free Trial
            </h4>
            <p className="text-sm font-light text-white/60">
              Try any plan free for 14 days. No credit card required.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}