'use client';

import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { Loader2, Lock, CreditCard } from 'lucide-react';
import { useState } from 'react';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { paymentService } from '@/lib/api/payment.service';
import { useAuthStore } from '@/lib/stores/auth.store';
import { getStripe, PRICING_PLANS, type PricingPlan, formatPrice } from '@/lib/stripe/client';

interface CheckoutFormProps {
  planId: PricingPlan;
  customerEmail?: string | undefined;
  onSuccess?: (sessionId: string) => void | undefined;
  onError?: (error: string) => void | undefined;
}

// Inner form component that uses Stripe hooks
function CheckoutFormInner({ planId, customerEmail, onSuccess, onError }: CheckoutFormProps) {
  const stripe = useStripe();
  const elements = useElements();
  const user = useAuthStore((state) => state.user);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState(customerEmail || user?.email || '');

  const plan = PRICING_PLANS[planId];

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) {
      setError('Payment system not ready. Please try again.');
      return;
    }

    if (!email) {
      setError('Please enter your email address.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Submit the payment element
      const { error: submitError } = await elements.submit();
      if (submitError) {
        setError(submitError.message || 'Payment failed');
        setIsLoading(false);
        return;
      }

      // Create checkout session via API
      const response = await paymentService.createCheckoutSession({
        plan_id: planId,
        success_url: `${window.location.origin}/dashboard?payment=success`,
        cancel_url: `${window.location.origin}/pricing?payment=cancelled`,
        trial_days: 30,
      });

      // Redirect to Stripe Checkout
      if (response.url) {
        window.location.href = response.url;
      } else if (response.session_id && stripe) {
        const { error: stripeError } = await stripe.redirectToCheckout({
          sessionId: response.session_id,
        });

        if (stripeError) {
          setError(stripeError.message || 'Payment failed');
        }
      }

      onSuccess?.(response.session_id);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
      onError?.(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        {/* Plan Summary */}
        <div className="rounded-lg bg-muted/50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">{plan.name} Plan</h3>
              <p className="text-sm text-muted-foreground">
                30-day free trial, then {formatPrice(plan.price)}/{plan.interval}
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gold">{formatPrice(plan.price)}</div>
              <div className="text-sm text-muted-foreground">per {plan.interval}</div>
            </div>
          </div>
        </div>

        {/* Email Input */}
        <div className="space-y-2">
          <Label htmlFor="email">Email Address</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            required
          />
        </div>

        {/* Payment Element */}
        <div className="space-y-2">
          <Label className="flex items-center gap-2">
            <CreditCard className="h-4 w-4" />
            Payment Details
          </Label>
          <div className="rounded-md border border-input p-3">
            <PaymentElement
              options={{
                layout: 'tabs',
              }}
            />
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
        className="w-full bg-gold text-navy hover:bg-gold-dark"
        disabled={!stripe || !elements || isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Processing...
          </>
        ) : (
          <>
            <Lock className="mr-2 h-4 w-4" />
            Start Free Trial
          </>
        )}
      </Button>

      {/* Security Notice */}
      <div className="text-center">
        <p className="text-xs text-muted-foreground">
          <Lock className="mr-1 inline h-3 w-3" />
          Secure payment powered by Stripe • No charges during trial
        </p>
      </div>
    </form>
  );
}

// Main checkout form component with Stripe Elements wrapper
export function CheckoutForm({ planId, customerEmail, onSuccess, onError }: CheckoutFormProps) {
  const [loading] = useState(false);
  const [error] = useState<string | null>(null);

  const plan = PRICING_PLANS[planId];
  const stripePromise = getStripe();

  if (loading) {
    return (
      <Card className="mx-auto w-full max-w-md">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="mr-2 h-6 w-6 animate-spin" />
          <span>Loading payment form...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="mx-auto w-full max-w-md">
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
    mode: 'subscription' as const,
    amount: plan.price * 100, // Convert to cents
    currency: plan.currency,
    appearance: {
      theme: 'stripe' as const,
      variables: {
        colorPrimary: '#CB963E', // Gold
        colorBackground: '#ffffff',
        colorText: '#17255A', // Navy
        colorDanger: '#DC3545',
        fontFamily: 'Inter, system-ui, sans-serif',
        spacingUnit: '4px',
        borderRadius: '6px',
      },
    },
  };

  return (
    <Card className="mx-auto w-full max-w-md">
      <CardHeader>
        <CardTitle>Complete Your Subscription</CardTitle>
        <CardDescription>Subscribe to {plan.name} plan with a 30-day free trial</CardDescription>
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
