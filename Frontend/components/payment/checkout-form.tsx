"use client";

import { useState, useEffect } from "react";
import { Elements, PaymentElement, useStripe, useElements } from "@stripe/react-stripe-js";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Lock, CreditCard } from "lucide-react";
import { getStripe, PRICING_PLANS, PricingPlan, formatPrice } from "@/lib/stripe-client";
import { apiClient } from "@/lib/api-client";

interface CheckoutFormProps {
  planId: PricingPlan;
  customerEmail?: string;
  onSuccess?: (subscriptionId: string) => void;
  onError?: (error: string) => void;
}

// Inner form component that uses Stripe hooks
function CheckoutFormInner({ planId, customerEmail, onSuccess, onError }: CheckoutFormProps) {
  const stripe = useStripe();
  const elements = useElements();
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState(customerEmail || "");
  
  const plan = PRICING_PLANS[planId];

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!stripe || !elements) {
      setError("Payment system not ready. Please try again.");
      return;
    }

    if (!email) {
      setError("Please enter your email address.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Create the subscription on your backend
      const { error: submitError } = await elements.submit();
      if (submitError) {
        setError(submitError.message || "Payment failed");
        setIsLoading(false);
        return;
      }

      // Create checkout session via your API
      const response = await apiClient.request('/api/payments/create-checkout-session', {
        method: 'POST',
        body: JSON.stringify({
          planId,
          customerEmail: email,
          successUrl: `${window.location.origin}/dashboard?payment=success`,
          cancelUrl: `${window.location.origin}/pricing?payment=cancelled`
        })
      });

      // Redirect to Stripe Checkout
      const { error: stripeError } = await stripe.redirectToCheckout({
        sessionId: response.sessionId
      });

      if (stripeError) {
        setError(stripeError.message || "Payment failed");
      }

    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
      onError?.(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        {/* Plan Summary */}
        <div className="bg-muted/50 p-4 rounded-lg">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="font-semibold">{plan.name} Plan</h3>
              <p className="text-sm text-muted-foreground">
                30-day free trial, then {formatPrice(plan.price)}/{plan.interval}
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">
                {formatPrice(plan.price)}
              </div>
              <div className="text-sm text-muted-foreground">per {plan.interval}</div>
            </div>
          </div>
        </div>

        {/* Email Input */}
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium">
            Email Address
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
            required
          />
        </div>

        {/* Payment Element */}
        <div className="space-y-2">
          <label className="text-sm font-medium flex items-center gap-2">
            <CreditCard className="w-4 h-4" />
            Payment Details
          </label>
          <div className="border border-input rounded-md p-3">
            <PaymentElement />
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Submit Button */}
      <Button
        type="submit"
        size="lg"
        className="w-full"
        disabled={!stripe || !elements || isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Processing...
          </>
        ) : (
          <>
            <Lock className="w-4 h-4 mr-2" />
            Start Free Trial
          </>
        )}
      </Button>

      {/* Security Notice */}
      <div className="text-center">
        <p className="text-xs text-muted-foreground">
          <Lock className="w-3 h-3 inline mr-1" />
          Secure payment powered by Stripe • No charges during trial
        </p>
      </div>
    </form>
  );
}

// Main checkout form component with Stripe Elements wrapper
export function CheckoutForm({ planId, customerEmail, onSuccess, onError }: CheckoutFormProps) {
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const plan = PRICING_PLANS[planId];
  const stripePromise = getStripe();

  useEffect(() => {
    // Create payment intent when component mounts
    const createPaymentIntent = async () => {
      try {
        const response = await apiClient.request('/api/payments/create-payment-intent', {
          method: 'POST',
          body: JSON.stringify({
            planId,
            customerEmail: customerEmail || ''
          })
        });
        
        setClientSecret(response.clientSecret);
      } catch (err: any) {
        setError(err.message || 'Failed to initialize payment');
        onError?.(err.message);
      } finally {
        setLoading(false);
      }
    };

    createPaymentIntent();
  }, [planId, customerEmail, onError]);

  if (loading) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin mr-2" />
          <span>Loading payment form...</span>
        </CardContent>
      </Card>
    );
  }

  if (error || !clientSecret) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Payment Error</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              {error || 'Failed to load payment form. Please try again.'}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const stripeOptions = {
    clientSecret,
    appearance: {
      theme: 'stripe' as const,
      variables: {
        colorPrimary: '#0F172A',
        colorBackground: '#ffffff',
        colorText: '#1a1a1a',
        colorDanger: '#df1b41',
        fontFamily: 'system-ui, sans-serif',
        spacingUnit: '4px',
        borderRadius: '6px'
      }
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Complete Your Subscription</CardTitle>
        <CardDescription>
          Subscribe to {plan.name} plan with a 30-day free trial
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Elements stripe={stripePromise} options={stripeOptions}>
          <CheckoutFormInner 
            planId={planId}
            customerEmail={customerEmail}
            onSuccess={onSuccess}
            onError={onError}
          />
        </Elements>
      </CardContent>
    </Card>
  );
}

export default CheckoutForm;