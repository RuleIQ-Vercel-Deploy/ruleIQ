"use client"

import { CheckCircle } from "lucide-react"
import { useEffect, useState } from "react"

import { PricingSection } from "@/components/payment/pricing-card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { paymentService } from "@/lib/api/payment.service"


import type { PricingPlan } from "@/lib/stripe/client"

export default function PricingPage() {
  const [currentPlan, setCurrentPlan] = useState<PricingPlan | undefined>()
  const [loading, setLoading] = useState(true)


  useEffect(() => {
    fetchCurrentSubscription()
  }, [])

  const fetchCurrentSubscription = async () => {
    try {
      const subscription = await paymentService.getCurrentSubscription()
      if (subscription) {
        setCurrentPlan(subscription.plan_id)
      }
    } catch (error) {
      console.error('Error fetching subscription:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectPlan = async (planId: PricingPlan) => {
    try {
      // Ensure we're on the client side
      if (typeof window === 'undefined') return

      // Create checkout session
      const response = await paymentService.createCheckoutSession({
        plan_id: planId,
        success_url: `${window.location.origin}/dashboard?payment=success`,
        cancel_url: `${window.location.origin}/pricing?payment=cancelled`,
        trial_days: 30
      })

      // Redirect to Stripe Checkout
      if (response.url) {
        window.location.href = response.url
      }
    } catch (error) {
      console.error('Error creating checkout session:', error)
    }
  }

  // Check for payment status in URL (client-side only)
  const [paymentStatus, setPaymentStatus] = useState<string | null>(null)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const searchParams = new URLSearchParams(window.location.search)
      setPaymentStatus(searchParams.get('payment'))
    }
  }, [])

  return (
    <div className="flex-1 space-y-8 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-navy mb-4">
            Choose the Perfect Plan for Your Business
          </h1>
          <p className="text-xl text-muted-foreground">
            Start your compliance journey with a 30-day free trial
          </p>
        </div>

        {/* Payment Status Alert */}
        {paymentStatus === 'cancelled' && (
          <Alert className="mb-8 max-w-2xl mx-auto">
            <AlertDescription>
              Your payment was cancelled. No charges were made. Feel free to try again when you're ready.
            </AlertDescription>
          </Alert>
        )}

        {paymentStatus === 'success' && (
          <Alert className="mb-8 max-w-2xl mx-auto border-success">
            <CheckCircle className="h-4 w-4 text-success" />
            <AlertDescription>
              Payment successful! Your subscription is now active. Welcome to ruleIQ!
            </AlertDescription>
          </Alert>
        )}

        {/* Current Plan Info */}
        {currentPlan && !loading && (
          <div className="text-center mb-8">
            <p className="text-sm text-muted-foreground">
              You are currently on the <span className="font-semibold text-gold">{currentPlan}</span> plan
            </p>
          </div>
        )}

        {/* Pricing Cards */}
        <PricingSection 
          onSelectPlan={handleSelectPlan}
          {...(currentPlan && { currentPlan })}
          showHeader={false}
        />

        {/* FAQ Section */}
        <div className="mt-16 max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-navy text-center mb-8">
            Frequently Asked Questions
          </h2>
          
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">Can I change plans later?</h3>
              <p className="text-muted-foreground">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2">What happens after the free trial?</h3>
              <p className="text-muted-foreground">
                After your 30-day free trial, you'll be charged the monthly subscription fee. You can cancel anytime during the trial.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2">Do you offer annual billing?</h3>
              <p className="text-muted-foreground">
                Yes, we offer a 20% discount for annual billing. Contact our sales team to learn more.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
              <p className="text-muted-foreground">
                We accept all major credit cards, debit cards, and bank transfers through Stripe.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}