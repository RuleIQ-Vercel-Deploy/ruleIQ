'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowRight, Loader2, Mail, Building, Users } from 'lucide-react';
import { freemiumService, type LeadCaptureRequest } from '@/lib/api/freemium.service';

interface EmailCaptureFormProps {
  onSuccess: (leadId: string, email: string) => void;
  className?: string;
  variant?: 'inline' | 'modal' | 'hero';
}

export function EmailCaptureForm({ onSuccess, className = '', variant = 'hero' }: EmailCaptureFormProps) {
  const [formData, setFormData] = useState<Partial<LeadCaptureRequest>>({
    email: '',
    first_name: '',
    last_name: '',
    company_name: '',
    company_size: undefined,
    industry: '',
    marketing_consent: false,
    newsletter_subscribed: true,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Basic validation
      if (!formData.email) {
        throw new Error('Email is required');
      }

      // Add UTM parameters from URL if available
      const urlParams = new URLSearchParams(window.location.search);
      const utmData = {
        utm_source: urlParams.get('utm_source') || undefined,
        utm_medium: urlParams.get('utm_medium') || undefined,
        utm_campaign: urlParams.get('utm_campaign') || undefined,
        utm_term: urlParams.get('utm_term') || undefined,
        utm_content: urlParams.get('utm_content') || undefined,
      };

      const response = await freemiumService.captureEmail({
        ...formData,
        ...utmData,
      } as LeadCaptureRequest);
    // TODO: Replace with proper logging

    // TODO: Replace with proper logging
      onSuccess(response.lead_id, response.email);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to capture email');
    } finally {
      setIsLoading(false);
    }
  };

  const updateFormData = (field: keyof LeadCaptureRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (variant === 'inline') {
    return (
      <form onSubmit={handleSubmit} className={`flex gap-2 ${className}`}>
        <Input
          type="email"
          placeholder="Enter your email"
          value={formData.email}
          onChange={(e) => updateFormData('email', e.target.value)}
          className="flex-1"
          required
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Start Assessment'}
        </Button>
        {error && (
          <Alert className="mt-2">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </form>
    );
  }

  return (
    <form onSubmit={handleSubmit} className={`space-y-4 ${className}`}>
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <Label htmlFor="first_name">First Name</Label>
          <Input
            id="first_name"
            type="text"
            value={formData.first_name}
            onChange={(e) => updateFormData('first_name', e.target.value)}
            className="mt-1"
          />
        </div>

        <div>
          <Label htmlFor="last_name">Last Name</Label>
          <Input
            id="last_name"
            type="text"
            value={formData.last_name}
            onChange={(e) => updateFormData('last_name', e.target.value)}
            className="mt-1"
          />
        </div>
      </div>

      <div>
        <Label htmlFor="email">Email Address *</Label>
        <div className="relative mt-1">
          <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => updateFormData('email', e.target.value)}
            className="pl-10"
            placeholder="your@company.com"
            required
          />
        </div>
      </div>

      <div>
        <Label htmlFor="company_name">Company Name</Label>
        <div className="relative mt-1">
          <Building className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            id="company_name"
            type="text"
            value={formData.company_name}
            onChange={(e) => updateFormData('company_name', e.target.value)}
            className="pl-10"
            placeholder="Your Company Ltd"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <Label htmlFor="company_size">Company Size</Label>
          <Select onValueChange={(value) => updateFormData('company_size', value)}>
            <SelectTrigger className="mt-1">
              <Users className="h-4 w-4 text-muted-foreground mr-2" />
              <SelectValue placeholder="Select size" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1-10">1-10 employees</SelectItem>
              <SelectItem value="11-50">11-50 employees</SelectItem>
              <SelectItem value="51-200">51-200 employees</SelectItem>
              <SelectItem value="201-500">201-500 employees</SelectItem>
              <SelectItem value="500+">500+ employees</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="industry">Industry</Label>
          <Input
            id="industry"
            type="text"
            value={formData.industry}
            onChange={(e) => updateFormData('industry', e.target.value)}
            className="mt-1"
            placeholder="e.g., Technology, Finance"
          />
        </div>
      </div>

      <div className="flex items-start space-x-2">
        <Checkbox
          id="newsletter"
          checked={formData.newsletter_subscribed}
          onCheckedChange={(checked) => updateFormData('newsletter_subscribed', !!checked)}
        />
        <Label htmlFor="newsletter" className="text-sm leading-5">
          Subscribe to our newsletter for compliance insights and updates
        </Label>
      </div>

      <div className="flex items-start space-x-2">
        <Checkbox
          id="marketing_consent"
          checked={formData.marketing_consent}
          onCheckedChange={(checked) => updateFormData('marketing_consent', !!checked)}
        />
        <Label htmlFor="marketing_consent" className="text-sm leading-5">
          I consent to receiving marketing communications from ruleIQ
        </Label>
      </div>

      <Button 
        type="submit" 
        className="w-full group" 
        size="lg"
        disabled={isLoading || !formData.email}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Starting Assessment...
          </>
        ) : (
          <>
            Start Free AI Assessment
            <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
          </>
        )}
      </Button>

      <p className="text-xs text-muted-foreground text-center">
        By submitting this form, you agree to our{' '}
        <a href="/privacy" className="underline hover:text-foreground">Privacy Policy</a>
        {' '}and{' '}
        <a href="/terms" className="underline hover:text-foreground">Terms of Service</a>
      </p>
    </form>
  );
}