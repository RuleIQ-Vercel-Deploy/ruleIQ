'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

import { AppSidebar } from '@/components/navigation/app-sidebar';
import { BreadcrumbNav } from '@/components/navigation/breadcrumb-nav';
import { GenerationProgress } from '@/components/policies/wizard/generation-progress';
import { SelectionCard } from '@/components/policies/wizard/selection-card';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { FormField } from '@/components/ui/form-field';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Stepper } from '@/components/ui/stepper';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import {
  frameworks,
  policyTypes,
  companyDetails,
  scopeOptions,
} from '@/lib/data/policy-wizard-data';
import { policyService } from '@/lib/api/policies.service';

const steps = ['Framework', 'Policy Type', 'Customize', 'Generate'];

export default function NewPolicyPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = React.useState(1);
  const [selectedFrameworks, setSelectedFrameworks] = React.useState<string[]>([]);
  const [selectedPolicyType, setSelectedPolicyType] = React.useState<string | null>(null);
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [companyName, setCompanyName] = React.useState(companyDetails.name);
  const [selectedScopes, setSelectedScopes] = React.useState<string[]>([]);
  const [additionalRequirements, setAdditionalRequirements] = React.useState('');

  const handleNext = async () => {
    if (currentStep === 3) {
      // Step 3: Generate the policy by calling the API
      await handleGeneratePolicy();
    } else {
      // Steps 1-2: Just move to the next step
      setCurrentStep((prev) => Math.min(prev + 1, steps.length));
    }
  };

  const handleBack = () => setCurrentStep((prev) => Math.max(prev - 1, 1));

  const handleGeneratePolicy = async () => {
    if (selectedFrameworks.length === 0 || !selectedPolicyType) {
      toast({
        title: 'Missing Information',
        description: 'Please select at least one framework and a policy type.',
        variant: 'destructive',
      });
      return;
    }

    setIsGenerating(true);
    setCurrentStep(4); // Move to progress step

    try {
      // Prepare custom requirements
      const customReqs = [];
      if (companyName !== companyDetails.name) {
        customReqs.push(`Company name: ${companyName}`);
      }
      if (selectedScopes.length > 0) {
        customReqs.push(`Policy scope: ${selectedScopes.join(', ')}`);
      }
      if (additionalRequirements.trim()) {
        customReqs.push(additionalRequirements.trim());
      }

      // Call the API with the first selected framework for now
      const generatedPolicy = await policyService.generatePolicy({
        framework_id: selectedFrameworks[0],
        policy_type: selectedPolicyType as 'comprehensive' | 'basic' | 'custom',
        custom_requirements: customReqs.length > 0 ? customReqs : undefined,
      });

      // Success - redirect to the policy view
      toast({
        title: 'Policy Generated Successfully',
        description: 'Your compliance policy has been generated and is ready for review.',
      });

      // Redirect to the generated policy
      router.push(`/policies/${generatedPolicy.id}`);
    } catch {
      // TODO: Replace with proper logging

      // // TODO: Replace with proper logging
      setIsGenerating(false);
      setCurrentStep(3); // Go back to customization step

      toast({
        title: 'Generation Failed',
        description: 'Failed to generate the policy. Please try again or contact support.',
        variant: 'destructive',
      });
    }
  };

  const toggleFramework = (id: string) => {
    setSelectedFrameworks((prev) =>
      prev.includes(id) ? prev.filter((fwId) => fwId !== id) : [...prev, id],
    );
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1: // Framework Selection
        return (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {frameworks.map((fw) => (
              <SelectionCard
                key={fw.id}
                title={fw.name}
                description={fw.description}
                icon={fw.icon}
                isSelected={selectedFrameworks.includes(fw.id)}
                onClick={() => toggleFramework(fw.id)}
              />
            ))}
          </div>
        );
      case 2: // Policy Type Selection
        return (
          <div className="grid grid-cols-2 gap-6 md:grid-cols-3 lg:grid-cols-4">
            {policyTypes.map((pt) => (
              <SelectionCard
                key={pt.id}
                title={pt.name}
                icon={pt.icon}
                isSelected={selectedPolicyType === pt.id}
                onClick={() => setSelectedPolicyType(pt.id)}
                className="flex aspect-square flex-col items-center justify-center text-center"
              />
            ))}
          </div>
        );
      case 3: // Customization Form
        return (
          <form className="max-w-3xl space-y-8">
            <FormField label="Company Name" description="This will be used in the policy document.">
              <Input value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
            </FormField>
            <div className="space-y-3">
              <Label>Policy Scope</Label>
              <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
                {scopeOptions.map((scope) => (
                  <div key={scope} className="flex items-center space-x-2">
                    <Checkbox
                      id={`scope-${scope}`}
                      checked={selectedScopes.includes(scope)}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          setSelectedScopes((prev) => [...prev, scope]);
                        } else {
                          setSelectedScopes((prev) => prev.filter((s) => s !== scope));
                        }
                      }}
                    />
                    <Label htmlFor={`scope-${scope}`} className="text-eggshell-white font-normal">
                      {scope}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
            <FormField
              label="Additional Requirements"
              description="Specify any custom clauses or requirements you need to include."
            >
              <Textarea
                placeholder="e.g., All data must be stored within the EU."
                rows={5}
                value={additionalRequirements}
                onChange={(e) => setAdditionalRequirements(e.target.value)}
              />
            </FormField>
          </form>
        );
      case 4: // Generation Progress
        return (
          <div className="mx-auto max-w-3xl">
            <GenerationProgress isGenerating={isGenerating} />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex min-h-screen w-full">
      <AppSidebar />
      <main className="flex flex-1 flex-col space-y-6 p-6 lg:p-8">
        <BreadcrumbNav
          items={[{ title: 'Policies', href: '/policies' }, { title: 'New Policy' }]}
        />
        <div className="flex w-full flex-1 flex-col">
          <div className="mb-8 space-y-2 text-center">
            <h1 className="text-eggshell-white text-3xl font-bold">Policy Generation Wizard</h1>
            <p className="text-grey-600 text-lg">
              Create a new compliance policy in just a few steps.
            </p>
          </div>

          <div className="mb-12">
            <Stepper steps={steps} currentStep={currentStep} />
          </div>

          <div className="flex-1">{renderStepContent()}</div>

          {currentStep < 4 && (
            <div className="mt-12 flex justify-between border-t border-white/10 pt-6">
              <Button
                variant="secondary"
                onClick={handleBack}
                disabled={currentStep === 1 || isGenerating}
              >
                Back
              </Button>
              <Button
                variant="default"
                onClick={handleNext}
                disabled={
                  isGenerating ||
                  (currentStep === 1 && selectedFrameworks.length === 0) ||
                  (currentStep === 2 && !selectedPolicyType)
                }
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : currentStep === 3 ? (
                  'Generate Policy'
                ) : (
                  'Next'
                )}
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
