"use client";

import { motion, AnimatePresence } from "framer-motion";
import { 
  Bot, 
  ChevronRight, 
  ChevronLeft,
  Save,
  AlertTriangle,
  Shield,
  Users,
  Building2,
  Globe,
  FileCheck,
  Lock,
  TrendingUp,
  Sparkles,
  Check,
  Loader2
} from "lucide-react";
import { useRouter } from "next/navigation";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { useAppStore } from "@/lib/stores/app.store";
import { cn } from "@/lib/utils";


// Question types
type QuestionType = "single-choice" | "multi-choice" | "text" | "number" | "scale";

interface Question {
  id: string;
  type: QuestionType;
  question: string;
  description?: string;
  options?: string[];
  validation?: string;
  required?: boolean;
  icon?: React.ReactNode;
  category: string;
}

// Question categories
const questionCategories = [
  { id: "business", name: "Business Overview", icon: <Building2 className="h-5 w-5" /> },
  { id: "data", name: "Data & Privacy", icon: <Lock className="h-5 w-5" /> },
  { id: "security", name: "Security", icon: <Shield className="h-5 w-5" /> },
  { id: "compliance", name: "Compliance", icon: <FileCheck className="h-5 w-5" /> },
  { id: "risk", name: "Risk Assessment", icon: <AlertTriangle className="h-5 w-5" /> },
];

// Questions bank
const questions: Question[] = [
  // Business Overview
  {
    id: "company_size",
    type: "single-choice",
    category: "business",
    question: "How many employees does your organization have?",
    options: ["1-10", "11-50", "51-200", "201-500", "500+"],
    required: true,
    icon: <Users className="h-5 w-5" />
  },
  {
    id: "industry",
    type: "single-choice",
    category: "business",
    question: "What is your primary industry?",
    options: ["Technology", "Healthcare", "Financial Services", "Retail", "Manufacturing", "Education", "Other"],
    required: true,
    icon: <Building2 className="h-5 w-5" />
  },
  {
    id: "locations",
    type: "multi-choice",
    category: "business",
    question: "Where does your business operate?",
    description: "Select all regions that apply",
    options: ["UK", "EU", "USA", "Asia", "Other"],
    required: true,
    icon: <Globe className="h-5 w-5" />
  },
  
  // Data & Privacy
  {
    id: "personal_data",
    type: "single-choice",
    category: "data",
    question: "Do you process personal data?",
    options: ["Yes", "No", "Not sure"],
    required: true,
    icon: <Lock className="h-5 w-5" />
  },
  {
    id: "data_types",
    type: "multi-choice",
    category: "data",
    question: "What types of personal data do you process?",
    description: "Select all that apply",
    options: ["Names & Contact Info", "Financial Data", "Health Records", "Employee Data", "Children's Data", "Biometric Data"],
    required: false,
    icon: <FileCheck className="h-5 w-5" />
  },
  {
    id: "data_volume",
    type: "single-choice",
    category: "data",
    question: "How many individuals' data do you process?",
    options: ["Less than 1,000", "1,000-10,000", "10,000-100,000", "More than 100,000"],
    required: false,
    icon: <Users className="h-5 w-5" />
  },
  
  // Security
  {
    id: "security_measures",
    type: "multi-choice",
    category: "security",
    question: "Which security measures do you currently have?",
    options: ["Encryption", "Access Controls", "Regular Backups", "Security Training", "Incident Response Plan", "None"],
    required: true,
    icon: <Shield className="h-5 w-5" />
  },
  {
    id: "security_incidents",
    type: "single-choice",
    category: "security",
    question: "Have you experienced any security incidents in the past year?",
    options: ["No incidents", "1-2 minor incidents", "3+ incidents", "Major breach"],
    required: true,
    icon: <AlertTriangle className="h-5 w-5" />
  },
  
  // Compliance
  {
    id: "current_frameworks",
    type: "multi-choice",
    category: "compliance",
    question: "Which compliance frameworks are you currently following?",
    options: ["GDPR", "ISO 27001", "SOC 2", "PCI DSS", "HIPAA", "Cyber Essentials", "None"],
    required: true,
    icon: <FileCheck className="h-5 w-5" />
  },
  {
    id: "compliance_goals",
    type: "multi-choice",
    category: "compliance",
    question: "What are your compliance goals for the next 12 months?",
    options: ["GDPR Compliance", "ISO 27001 Certification", "SOC 2 Attestation", "Cyber Essentials", "Other"],
    required: true,
    icon: <TrendingUp className="h-5 w-5" />
  },
  
  // Risk Assessment
  {
    id: "risk_appetite",
    type: "scale",
    category: "risk",
    question: "What is your organization's risk appetite?",
    description: "1 = Very Low (Risk Averse), 5 = Very High (Risk Tolerant)",
    options: ["1", "2", "3", "4", "5"],
    required: true,
    icon: <AlertTriangle className="h-5 w-5" />
  },
  {
    id: "biggest_concerns",
    type: "multi-choice",
    category: "risk",
    question: "What are your biggest compliance concerns?",
    options: ["Data breaches", "Regulatory fines", "Reputation damage", "Operational disruption", "Legal liability"],
    required: true,
    icon: <AlertTriangle className="h-5 w-5" />
  }
];

export default function ComplianceWizardPage() {
  const router = useRouter();
  const { addNotification } = useAppStore();
  
  const [currentCategoryIndex, setCurrentCategoryIndex] = React.useState(0);
  const [answers, setAnswers] = React.useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = React.useState(false);
  
  const currentCategory = questionCategories[currentCategoryIndex];
  const categoryQuestions = currentCategory ? questions.filter(q => q.category === currentCategory.id) : [];
  
  // Calculate overall progress
  const totalQuestions = questions.length;
  const answeredQuestions = Object.keys(answers).length;
  const progress = (answeredQuestions / totalQuestions) * 100;
  
  // Check if current category is complete
  const isCategoryComplete = () => {
    const requiredQuestions = categoryQuestions.filter(q => q.required);
    return requiredQuestions.every(q => answers[q.id] !== undefined && answers[q.id] !== "");
  };
  
  const handleAnswer = (questionId: string, value: any) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };
  
  const handleNext = () => {
    if (currentCategoryIndex < questionCategories.length - 1) {
      setCurrentCategoryIndex(currentCategoryIndex + 1);
    } else {
      handleComplete();
    }
  };
  
  const handleBack = () => {
    if (currentCategoryIndex > 0) {
      setCurrentCategoryIndex(currentCategoryIndex - 1);
    }
  };
  
  const handleComplete = async () => {
    setIsLoading(true);
    
    try {
      // Generate compliance report based on answers
      const report = generateComplianceReport(answers);
      
      // Store in localStorage for other components to use
      localStorage.setItem('compliance_assessment', JSON.stringify({
        answers,
        report,
        completedAt: new Date().toISOString()
      }));
      
      addNotification({
        type: "success",
        title: "Assessment Complete!",
        message: `Your compliance score is ${report.score}%. Check your personalized recommendations.`,
        duration: 5000,
      });
      
      // Redirect to results page
      router.push("/compliance-wizard/results");
    } catch (error) {
      addNotification({
        type: "error",
        title: "Error",
        message: "Failed to complete assessment. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const generateComplianceReport = (answers: Record<string, any>) => {
    let score = 0;
    let maxScore = 0;
    const recommendations: string[] = [];
    const risks: string[] = [];
    
    // Calculate score based on answers
    if (answers['security_measures'] && !answers['security_measures'].includes("None")) {
      score += answers['security_measures'].length * 5;
    }
    maxScore += 30;
    
    if (answers['current_frameworks'] && !answers['current_frameworks'].includes("None")) {
      score += answers['current_frameworks'].length * 10;
    }
    maxScore += 70;
    
    if (answers['security_incidents'] === "No incidents") {
      score += 20;
    }
    maxScore += 20;
    
    // Generate recommendations
    if (!answers['current_frameworks']?.includes("GDPR") && answers['locations']?.includes("EU")) {
      recommendations.push("Implement GDPR compliance as you operate in the EU");
      risks.push("Non-compliance with GDPR regulations");
    }
    
    if (answers['personal_data'] === "Yes" && !answers['security_measures']?.includes("Encryption")) {
      recommendations.push("Implement encryption for personal data protection");
      risks.push("Unencrypted personal data");
    }
    
    const finalScore = Math.round((score / maxScore) * 100);
    
    return {
      score: finalScore,
      recommendations,
      risks,
      maturityLevel: finalScore > 80 ? "Advanced" : finalScore > 50 ? "Intermediate" : "Beginner"
    };
  };
  
  const renderQuestion = (question: Question) => {
    const value = answers[question.id];
    
    switch (question.type) {
      case "single-choice":
        return (
          <RadioGroup
            value={value || ""}
            onValueChange={(val) => handleAnswer(question.id, val)}
          >
            <div className="space-y-2">
              {question.options?.map((option) => (
                <div key={option} className="flex items-center space-x-2">
                  <RadioGroupItem value={option} id={`${question.id}-${option}`} />
                  <Label 
                    htmlFor={`${question.id}-${option}`}
                    className="cursor-pointer flex-1 py-2"
                  >
                    {option}
                  </Label>
                </div>
              ))}
            </div>
          </RadioGroup>
        );
        
      case "multi-choice":
        return (
          <div className="space-y-2">
            {question.options?.map((option) => (
              <div key={option} className="flex items-center space-x-2">
                <Checkbox
                  id={`${question.id}-${option}`}
                  checked={(value || []).includes(option)}
                  onCheckedChange={(checked) => {
                    const current = value || [];
                    if (checked) {
                      handleAnswer(question.id, [...current, option]);
                    } else {
                      handleAnswer(question.id, current.filter((v: string) => v !== option));
                    }
                  }}
                />
                <Label 
                  htmlFor={`${question.id}-${option}`}
                  className="cursor-pointer flex-1 py-2"
                >
                  {option}
                </Label>
              </div>
            ))}
          </div>
        );
        
      case "scale":
        return (
          <RadioGroup
            value={value || ""}
            onValueChange={(val) => handleAnswer(question.id, val)}
          >
            <div className="flex justify-between items-center">
              {question.options?.map((option) => (
                <div key={option} className="flex flex-col items-center">
                  <RadioGroupItem value={option} id={`${question.id}-${option}`} />
                  <Label 
                    htmlFor={`${question.id}-${option}`}
                    className="cursor-pointer mt-2"
                  >
                    {option}
                  </Label>
                </div>
              ))}
            </div>
          </RadioGroup>
        );
        
      case "text":
        return (
          <Input
            value={value || ""}
            onChange={(e) => handleAnswer(question.id, e.target.value)}
            placeholder="Enter your answer..."
          />
        );
        
      default:
        return null;
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-full bg-primary/10">
            <Bot className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Compliance Assessment Wizard</h1>
            <p className="text-muted-foreground">
              Let IQ understand your compliance needs and create a personalized roadmap
            </p>
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Overall Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      </div>
      
      <div className="grid lg:grid-cols-4 gap-6">
        {/* Category Navigation */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Categories</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {questionCategories.map((category, index) => {
                const categoryAnswered = questions
                  .filter(q => q.category === category.id && q.required)
                  .every(q => answers[q.id]);
                  
                return (
                  <button
                    key={category.id}
                    onClick={() => setCurrentCategoryIndex(index)}
                    className={cn(
                      "w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center gap-2",
                      currentCategoryIndex === index 
                        ? "bg-primary text-primary-foreground" 
                        : "hover:bg-muted",
                      categoryAnswered && "border-l-4 border-green-500"
                    )}
                  >
                    {category.icon}
                    <span className="text-sm font-medium">{category.name}</span>
                    {categoryAnswered && <Check className="h-4 w-4 ml-auto" />}
                  </button>
                );
              })}
            </CardContent>
          </Card>
        </div>
        
        {/* Questions */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                {currentCategory?.icon}
                <CardTitle>{currentCategory?.name}</CardTitle>
              </div>
              <CardDescription>
                Answer these questions to help us understand your {currentCategory?.name.toLowerCase()} requirements
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <AnimatePresence mode="wait">
                {categoryQuestions.map((question) => (
                  <motion.div
                    key={question.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="space-y-4 p-4 rounded-lg border"
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        {question.icon || <Sparkles className="h-5 w-5 text-primary" />}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium flex items-center gap-2">
                          {question.question}
                          {question.required && (
                            <Badge variant="secondary" className="text-xs">Required</Badge>
                          )}
                        </h3>
                        {question.description && (
                          <p className="text-sm text-muted-foreground mt-1">
                            {question.description}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="ml-11">
                      {renderQuestion(question)}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              <div className="flex justify-between pt-6">
                <Button
                  variant="outline"
                  onClick={handleBack}
                  disabled={currentCategoryIndex === 0}
                >
                  <ChevronLeft className="h-4 w-4 mr-2" />
                  Previous
                </Button>
                
                {currentCategoryIndex === questionCategories.length - 1 ? (
                  <Button
                    onClick={handleComplete}
                    disabled={!isCategoryComplete() || isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        Complete Assessment
                        <Sparkles className="h-4 w-4 ml-2" />
                      </>
                    )}
                  </Button>
                ) : (
                  <Button
                    onClick={handleNext}
                    disabled={!isCategoryComplete()}
                  >
                    Next
                    <ChevronRight className="h-4 w-4 ml-2" />
                  </Button>
                )}
              </div>
              
              <div className="text-center pt-4">
                <Button
                  variant="ghost"
                  onClick={() => {
                    localStorage.setItem('compliance_assessment_draft', JSON.stringify(answers));
                    addNotification({
                      type: "success",
                      title: "Progress Saved",
                      message: "Your answers have been saved. You can continue later.",
                    });
                    router.push("/dashboard");
                  }}
                >
                  <Save className="h-4 w-4 mr-2" />
                  Save & Exit
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}