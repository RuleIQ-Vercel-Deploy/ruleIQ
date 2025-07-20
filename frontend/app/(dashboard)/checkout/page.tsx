"use client"

import { Shield, Lock, CreditCard } from "lucide-react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"

import { CheckoutForm } from "@/components/payment/checkout-form"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuthStore } from "@/lib/stores/auth.store"
import { PRICING_PLANS, type PricingPlan, formatPrice } from "@/lib/stripe/client"


export default function CheckoutPage() {
  const searchParams = useSearchParams()
  const planId = searchParams?.get('plan') as PricingPlan
  const user = useAuthStore(state => state.user)
  
  // Validate plan ID
  if (!planId || !PRICING_PLANS[planId]) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle>Invalid Plan</CardTitle>
            <CardDescription>
              The selected plan is not valid. Please choose a plan from our pricing page.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/pricing">View Plans</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const plan = PRICING_PLANS[planId]

  const handleSuccess = (sessionId: string) => {
    // Redirect to success page or dashboard
    window.location.href = `/dashboard?payment=success&session_id=${sessionId}`
  }

  const handleError = (error: string) => {
    console.error('Checkout error:', error)
  }

  return (
    <div className="flex-1 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-navy mb-2">Complete Your Subscription</h1>
          <p className="text-muted-foreground">
            You're just one step away from automated compliance management
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Order Summary */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Plan Details */}
                <div>
                  <h3 className="font-semibold mb-4">Selected Plan</h3>
                  <div className="bg-muted/50 p-4 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-semibold">{plan.name} Plan</p>
                        <p className="text-sm text-muted-foreground">Monthly subscription</p>
                      </div>
                      <p className="font-semibold">{formatPrice(plan.price)}/mo</p>
                    </div>
                    <div className="text-sm text-success font-medium">
                      ✓ 30-day free trial included
                    </div>
                  </div>
                </div>

                {/* Features */}
                <div>
                  <h3 className="font-semibold mb-3">Included Features</h3>
                  <ul className="space-y-2">
                    {plan.features.slice(0, 5).map((feature, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <span className="text-gold mt-0.5">✓</span>
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Billing Summary */}
                <div className="border-t pt-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Subtotal</span>
                      <span>{formatPrice(plan.price)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>VAT (20%)</span>
                      <span>{formatPrice(plan.price * 0.2)}</span>
                    </div>
                    <div className="flex justify-between font-semibold">
                      <span>Total (after trial)</span>
                      <span>{formatPrice(plan.price * 1.2)}/mo</span>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    * You won't be charged until after your 30-day free trial ends
                  </p>
                </div>

                {/* Security Badges */}
                <div className="flex items-center justify-center gap-4 pt-4 border-t">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Shield className="h-4 w-4" />
                    <span>Secure</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Lock className="h-4 w-4" />
                    <span>Encrypted</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <CreditCard className="h-4 w-4" />
                    <span>PCI Compliant</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Checkout Form */}
          <div>
            <CheckoutForm
              planId={planId}
              {...(user?.email && { customerEmail: user.email })}
              onSuccess={handleSuccess}
              onError={handleError}
            />
          </div>
        </div>
      </div>
    </div>
  )
}