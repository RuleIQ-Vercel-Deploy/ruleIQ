"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check } from "lucide-react";
import { PRICING_PLANS, PricingPlan, formatPrice, isPlanPopular } from "@/lib/stripe-client";
import { useRouter } from "next/navigation";

interface PricingCardProps {
  planId: PricingPlan;
  onSelectPlan?: (planId: PricingPlan) => void;
  disabled?: boolean;
  currentPlan?: PricingPlan;
}

export function PricingCard({ planId, onSelectPlan, disabled = false, currentPlan }: PricingCardProps) {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const plan = PRICING_PLANS[planId];
  
  if (!plan) {
    return null;
  }

  const isCurrentPlan = currentPlan === planId;
  const isPopular = isPlanPopular(planId);

  const handleSelectPlan = async () => {
    if (disabled || isCurrentPlan) return;
    
    setIsLoading(true);
    
    try {
      if (onSelectPlan) {
        onSelectPlan(planId);
      } else {
        // Default behavior - redirect to checkout
        router.push(`/checkout?plan=${planId}`);
      }
    } catch (error) {
      console.error('Error selecting plan:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getButtonText = () => {
    if (isCurrentPlan) return "Current Plan";
    if (planId === 'enterprise') return "Contact Sales";
    if (plan.price === 0) return "Start Free Trial";
    return "Start Free Trial";
  };

  return (
    <Card className={`relative transition-all duration-300 hover:shadow-lg ${
      isPopular 
        ? 'border-primary shadow-md scale-105' 
        : 'border-border hover:border-primary/50'
    } ${isCurrentPlan ? 'bg-muted/50' : ''}`}>
      
      {isPopular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <Badge variant="default" className="bg-primary text-primary-foreground px-3 py-1">
            Most Popular
          </Badge>
        </div>
      )}

      <CardHeader className="text-center pb-2">
        <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
        <div className="mt-4">
          <span className="text-4xl font-bold">
            {plan.price === 0 ? 'Free' : formatPrice(plan.price)}
          </span>
          {plan.price > 0 && (
            <span className="text-muted-foreground text-lg">/{plan.interval}</span>
          )}
        </div>
        <CardDescription className="mt-2">
          {planId === 'starter' && "Perfect for small businesses getting started with compliance"}
          {planId === 'professional' && "Advanced features for growing businesses"}
          {planId === 'enterprise' && "Complete solution for large organizations"}
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-4">
        <div className="space-y-3">
          {plan.features.map((feature, index) => (
            <div key={index} className="flex items-start gap-3">
              <Check className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
              <span className="text-sm text-muted-foreground">{feature}</span>
            </div>
          ))}
        </div>
      </CardContent>

      <CardFooter className="pt-4">
        <Button
          className="w-full"
          variant={isCurrentPlan ? "secondary" : "default"}
          size="lg"
          onClick={handleSelectPlan}
          disabled={disabled || isLoading || isCurrentPlan}
        >
          {isLoading ? "Loading..." : getButtonText()}
        </Button>
        
        {!isCurrentPlan && plan.price > 0 && (
          <p className="text-xs text-muted-foreground text-center mt-2 w-full">
            30-day free trial • Cancel anytime
          </p>
        )}
      </CardFooter>
    </Card>
  );
}

// Pricing section component
interface PricingSectionProps {
  onSelectPlan?: (planId: PricingPlan) => void;
  currentPlan?: PricingPlan;
  showHeader?: boolean;
}

export function PricingSection({ onSelectPlan, currentPlan, showHeader = true }: PricingSectionProps) {
  return (
    <div className="py-16 px-4">
      {showHeader && (
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Choose Your Plan</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Start with a 30-day free trial. No credit card required.
          </p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
        <PricingCard 
          planId="starter" 
          onSelectPlan={onSelectPlan}
          currentPlan={currentPlan}
        />
        <PricingCard 
          planId="professional" 
          onSelectPlan={onSelectPlan}
          currentPlan={currentPlan}
        />
        <PricingCard 
          planId="enterprise" 
          onSelectPlan={onSelectPlan}
          currentPlan={currentPlan}
        />
      </div>
      
      <div className="text-center mt-12">
        <div className="inline-flex items-center gap-8 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-primary" />
            <span>30-day free trial</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-primary" />
            <span>Cancel anytime</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-primary" />
            <span>No setup fees</span>
          </div>
        </div>
      </div>
    </div>
  );
}