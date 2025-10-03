"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Settings, Sparkles } from 'lucide-react';

export function IntelligentPolicyWizard() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            Intelligent Policy Generation Wizard
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 border rounded-lg">
              <FileText className="w-12 h-12 mx-auto mb-4 text-purple-600" />
              <h3 className="font-semibold mb-2">Select Framework</h3>
              <p className="text-sm text-muted-foreground mb-4">Choose compliance framework (GDPR, SOC 2, ISO 27001)</p>
              <Button variant="outline" className="w-full">
                Choose Framework
              </Button>
            </div>
            
            <div className="text-center p-6 border rounded-lg">
              <Settings className="w-12 h-12 mx-auto mb-4 text-purple-600" />
              <h3 className="font-semibold mb-2">Configure Options</h3>
              <p className="text-sm text-muted-foreground mb-4">Customize policy requirements and scope</p>
              <Button variant="outline" className="w-full">
                Configure
              </Button>
            </div>
            
            <div className="text-center p-6 border rounded-lg">
              <Sparkles className="w-12 h-12 mx-auto mb-4 text-purple-600" />
              <h3 className="font-semibold mb-2">Generate Policy</h3>
              <p className="text-sm text-muted-foreground mb-4">AI-powered policy generation and review</p>
              <Button className="w-full">
                Generate
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}