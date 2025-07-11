"use client";

import { motion } from "framer-motion";
import { 
  Shield, 
  Clock, 
  FileText, 
  TrendingUp,
  CheckCircle,
  ArrowRight,
  Info,
  Zap,
  Award
} from "lucide-react";
import { useState } from "react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AssessmentUtils } from "@/lib/assessment-engine/utils";

export interface Framework {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  estimatedDuration: number;
  questionCount: number;
  coverageAreas: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  popularity: number;
  lastUpdated: string;
  icon?: React.ReactNode;
}

interface FrameworkSelectorProps {
  frameworks: Framework[];
  onSelect: (frameworkId: string, mode: 'quick' | 'comprehensive') => void;
  onCancel: () => void;
}

export function FrameworkSelector({
  frameworks,
  onSelect,
  onCancel
}: FrameworkSelectorProps) {
  const [selectedFramework, setSelectedFramework] = useState<string | null>(null);
  const [assessmentMode, setAssessmentMode] = useState<'quick' | 'comprehensive'>('comprehensive');
  const [category, setCategory] = useState<string>('all');

  // Group frameworks by category
  const categories = ['all', ...new Set(frameworks.map(f => f.category))];
  const filteredFrameworks = category === 'all' 
    ? frameworks 
    : frameworks.filter(f => f.category === category);

  // Sort by popularity
  const sortedFrameworks = [...filteredFrameworks].sort((a, b) => b.popularity - a.popularity);

  const handleStart = () => {
    if (selectedFramework) {
      onSelect(selectedFramework, assessmentMode);
    }
  };

  const getFrameworkIcon = (framework: Framework) => {
    if (framework.icon) return framework.icon;
    
    switch (framework.category) {
      case 'data-protection':
        return <Shield className="h-6 w-6" />;
      case 'security':
        return <Shield className="h-6 w-6" />;
      case 'quality':
        return <Award className="h-6 w-6" />;
      default:
        return <FileText className="h-6 w-6" />;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-navy mb-2">Select Compliance Framework</h1>
        <p className="text-muted-foreground">
          Choose the framework that best matches your compliance needs
        </p>
      </div>

      {/* Category Tabs */}
      <Tabs value={category} onValueChange={setCategory}>
        <TabsList className="grid w-full grid-cols-5">
          {categories.map((cat) => (
            <TabsTrigger key={cat} value={cat} className="capitalize">
              {cat === 'all' ? 'All Frameworks' : cat.replace('-', ' ')}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Framework Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {sortedFrameworks.map((framework) => {
          const isSelected = selectedFramework === framework.id;
          const estimatedTime = assessmentMode === 'quick' 
            ? Math.round(framework.estimatedDuration * 0.3) 
            : framework.estimatedDuration;

          return (
            <motion.div
              key={framework.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Card 
                className={`cursor-pointer transition-all ${
                  isSelected 
                    ? 'ring-2 ring-gold border-gold' 
                    : 'hover:shadow-lg'
                }`}
                onClick={() => setSelectedFramework(framework.id)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      {getFrameworkIcon(framework)}
                    </div>
                    {isSelected && (
                      <CheckCircle className="h-5 w-5 text-gold" />
                    )}
                  </div>
                  <CardTitle className="mt-4">{framework.name}</CardTitle>
                  <CardDescription className="line-clamp-2">
                    {framework.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {/* Stats */}
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        <span>{AssessmentUtils.formatDuration(estimatedTime)}</span>
                      </div>
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <FileText className="h-4 w-4" />
                        <span>{framework.questionCount} questions</span>
                      </div>
                    </div>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-1">
                      <Badge 
                        variant="outline" 
                        className={getDifficultyColor(framework.difficulty)}
                      >
                        {framework.difficulty}
                      </Badge>
                      {framework.tags.slice(0, 2).map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {framework.tags.length > 2 && (
                        <Badge variant="secondary" className="text-xs">
                          +{framework.tags.length - 2}
                        </Badge>
                      )}
                    </div>

                    {/* Coverage Areas */}
                    <div className="pt-2 border-t">
                      <p className="text-xs font-medium text-muted-foreground mb-1">
                        Coverage Areas:
                      </p>
                      <div className="text-xs text-muted-foreground">
                        {framework.coverageAreas.slice(0, 3).join(', ')}
                        {framework.coverageAreas.length > 3 && (
                          <span> +{framework.coverageAreas.length - 3} more</span>
                        )}
                      </div>
                    </div>

                    {/* Popularity */}
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-muted rounded-full h-2">
                        <div 
                          className="bg-gold h-2 rounded-full"
                          style={{ width: `${framework.popularity}%` }}
                        />
                      </div>
                      <TrendingUp className="h-3 w-3 text-gold" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Selected Framework Options */}
      {selectedFramework && (
        <Card>
          <CardHeader>
            <CardTitle>Assessment Options</CardTitle>
            <CardDescription>
              Choose how you'd like to complete this assessment
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <RadioGroup value={assessmentMode} onValueChange={(v) => setAssessmentMode(v as any)}>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="flex items-start space-x-2">
                  <RadioGroupItem value="quick" id="quick" />
                  <div className="flex-1">
                    <Label htmlFor="quick" className="cursor-pointer">
                      <div className="flex items-center gap-2 mb-1">
                        <Zap className="h-4 w-4 text-gold" />
                        <span className="font-medium">Quick Assessment</span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Get a rapid compliance overview with essential questions only. 
                        Perfect for initial evaluation or time-constrained situations.
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        ~{Math.round(frameworks.find(f => f.id === selectedFramework)!.estimatedDuration * 0.3)} minutes
                      </p>
                    </Label>
                  </div>
                </div>

                <div className="flex items-start space-x-2">
                  <RadioGroupItem value="comprehensive" id="comprehensive" />
                  <div className="flex-1">
                    <Label htmlFor="comprehensive" className="cursor-pointer">
                      <div className="flex items-center gap-2 mb-1">
                        <Shield className="h-4 w-4 text-primary" />
                        <span className="font-medium">Comprehensive Assessment</span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Complete evaluation covering all compliance areas. 
                        Provides detailed insights and actionable recommendations.
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        ~{frameworks.find(f => f.id === selectedFramework)!.estimatedDuration} minutes
                      </p>
                    </Label>
                  </div>
                </div>
              </div>
            </RadioGroup>

            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                You can save your progress at any time and resume later. 
                All assessments include detailed reports and recommendations upon completion.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between">
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button
          onClick={handleStart}
          disabled={!selectedFramework}
          className="bg-gold hover:bg-gold-dark text-navy"
        >
          Start Assessment
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}