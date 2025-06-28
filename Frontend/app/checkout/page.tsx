"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { CheckoutForm } from "@/components/payment/checkout-form";
import { PricingPlan, PRICING_PLANS } from "@/lib/stripe-client";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

function CheckoutContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [planId, setPlanId] = useState<PricingPlan | null>(null);

  useEffect(() => {
    const plan = searchParams.get('plan') as PricingPlan;
    if (plan && PRICING_PLANS[plan]) {
      setPlanId(plan);
    } else {
      // Redirect to pricing if no valid plan specified
      router.push('/pricing');
    }
  }, [searchParams, router]);

  const handlePaymentSuccess = (subscriptionId: string) => {
    router.push(`/dashboard?payment=success&subscription=${subscriptionId}`);
  };

  const handlePaymentError = (error: string) => {
    console.error('Payment error:', error);
    // Could show a toast notification or redirect to error page
  };

  if (!planId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Loading...</h1>
          <p className="text-muted-foreground">Preparing your checkout</p>
        </div>
      </div>
    );
  }

  const plan = PRICING_PLANS[planId];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/pricing">
            <Button variant="ghost" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Pricing
            </Button>
          </Link>
          
          <div className="text-center">
            <h1 className="text-3xl font-bold mb-2">Subscribe to NexCompli</h1>
            <p className="text-muted-foreground">
              You're subscribing to the <strong>{plan.name}</strong> plan
            </p>
          </div>
        </div>

        {/* Checkout Form */}
        <div className="flex justify-center">
          <CheckoutForm
            planId={planId}
            onSuccess={handlePaymentSuccess}
            onError={handlePaymentError}
          />
        </div>

        {/* Trust Indicators */}
        <div className="mt-12 text-center">
          <div className="flex justify-center items-center gap-8 text-sm text-muted-foreground">
            <div>🔒 256-bit SSL encrypted</div>
            <div>🛡️ PCI DSS compliant</div>
            <div>💳 Powered by Stripe</div>
          </div>
        </div>

        {/* FAQ */}
        <div className="mt-16 max-w-2xl mx-auto">
          <h2 className="text-xl font-semibold mb-6 text-center">Frequently Asked Questions</h2>
          <div className="space-y-4">
            <div className="border rounded-lg p-4">
              <h3 className="font-medium mb-2">When will I be charged?</h3>
              <p className="text-sm text-muted-foreground">
                You won't be charged during your 30-day free trial. After the trial ends, 
                you'll be charged {plan.price > 0 ? `${plan.price} GBP` : 'nothing'} per {plan.interval}.
              </p>
            </div>
            
            <div className="border rounded-lg p-4">
              <h3 className="font-medium mb-2">Can I cancel anytime?</h3>
              <p className="text-sm text-muted-foreground">
                Yes, you can cancel your subscription at any time. You'll continue to have 
                access until the end of your current billing period.
              </p>
            </div>
            
            <div className="border rounded-lg p-4">
              <h3 className="font-medium mb-2">Can I change plans later?</h3>
              <p className="text-sm text-muted-foreground">
                Absolutely! You can upgrade or downgrade your plan at any time from your 
                account dashboard.
              </p>
            </div>
            
            <div className="border rounded-lg p-4">
              <h3 className="font-medium mb-2">Is my payment information secure?</h3>
              <p className="text-sm text-muted-foreground">
                Yes, all payments are processed securely through Stripe, which is PCI DSS 
                compliant and used by millions of businesses worldwide.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense 
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Loading...</h1>
            <p className="text-muted-foreground">Preparing your checkout</p>
          </div>
        </div>
      }
    >
      <CheckoutContent />
    </Suspense>
  );
}