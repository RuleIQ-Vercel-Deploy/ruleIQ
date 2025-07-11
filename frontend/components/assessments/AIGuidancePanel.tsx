"use client";

import { motion, AnimatePresence } from "framer-motion";
import { 
  Bot, 
  ChevronDown, 
  ChevronUp, 
  Copy, 
  MessageSquare,
  Lightbulb,
  BookOpen,
  ExternalLink,
  RefreshCw
} from "lucide-react";
import React, { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { assessmentAIService, type AIHelpResponse } from "@/lib/api/assessments-ai.service";
import { type Question } from "@/lib/assessment-engine/types";
import { cn } from "@/lib/utils";
import { type UserContext } from "@/types/ai";

interface AIGuidancePanelProps {
  question: Question;
  frameworkId: string;
  sectionId?: string;
  userContext?: UserContext;
  className?: string;
  defaultOpen?: boolean;
}

export function AIGuidancePanel({
  question,
  frameworkId,
  sectionId,
  userContext,
  className,
  defaultOpen = false
}: AIGuidancePanelProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState<AIHelpResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);
  const { toast } = useToast();
  
  // Load guidance when defaultOpen is true
  React.useEffect(() => {
    if (defaultOpen && !aiResponse && !loading) {
      loadGuidance();
    }
  }, []);

  const loadGuidance = async () => {
    // Prevent multiple concurrent requests
    const currentRequestId = Date.now().toString();
    setRequestId(currentRequestId);
    setLoading(true);
    setError(null);

    try {
      const response = await assessmentAIService.getQuestionHelp({
        question_id: question.id,
        question_text: question.text,
        framework_id: frameworkId,
        section_id: sectionId,
        user_context: userContext
      });

      // Check if this request is still valid by checking the ref
      setRequestId((latestRequestId) => {
        if (currentRequestId === latestRequestId) {
          setAiResponse(response);
          setLoading(false);
        }
        return latestRequestId;
      });
    } catch (err) {
      setRequestId((latestRequestId) => {
        if (currentRequestId === latestRequestId) {
          setError(err instanceof Error ? err.message : 'Failed to load AI guidance');
          setLoading(false);
        }
        return latestRequestId;
      });
    }
  };

  const handleToggle = () => {
    if (!isOpen && !aiResponse && !loading) {
      loadGuidance();
    }
    setIsOpen(!isOpen);
  };

  const handleRefresh = () => {
    if (!loading) {
      setAiResponse(null);
      loadGuidance();
    }
  };

  const handleCopyGuidance = () => {
    if (aiResponse?.guidance) {
      navigator.clipboard.writeText(aiResponse.guidance);
      toast({
        title: "Guidance copied",
        description: "AI guidance has been copied to your clipboard.",
        duration: 2000
      });
    }
  };

  const handleCopyAll = () => {
    if (!aiResponse) return;

    const fullContent = [
      `AI Guidance for: ${question.text}`,
      '',
      aiResponse.guidance,
      '',
      ...(aiResponse.follow_up_suggestions ? [
        'Suggestions:',
        ...aiResponse.follow_up_suggestions.map(s => `• ${s}`),
        ''
      ] : []),
      ...(aiResponse.source_references ? [
        'References:',
        ...aiResponse.source_references.map(ref => `• ${ref}`)
      ] : [])
    ].join('\n');

    navigator.clipboard.writeText(fullContent);
    toast({
      title: "Full guidance copied",
      description: "Complete AI guidance has been copied to your clipboard.",
      duration: 2000
    });
  };

  return (
    <Card className={cn("border-l-4 border-l-primary", className)}>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <CardHeader 
            className="cursor-pointer hover:bg-muted/50 transition-colors"
            onClick={handleToggle}
          >
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Bot className="h-4 w-4 text-primary" />
                AI Compliance Guidance
                {aiResponse && (
                  <Badge variant="outline" className="text-xs">
                    {Math.round(aiResponse.confidence_score * 100)}% confidence
                  </Badge>
                )}
              </CardTitle>
              <div 
                className="p-1"
                onClick={(e) => e.stopPropagation()}
              >
                {isOpen ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </div>
            </div>
          </CardHeader>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="pt-0">
            <AnimatePresence mode="wait">
              {loading && (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center py-8"
                >
                  <Bot className="h-8 w-8 animate-pulse text-primary mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground">
                    Analyzing compliance requirements...
                  </p>
                </motion.div>
              )}

              {error && (
                <motion.div
                  key="error"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-center py-6"
                >
                  <p className="text-sm text-destructive mb-3">{error}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={loadGuidance}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Try Again
                  </Button>
                </motion.div>
              )}

              {aiResponse && (
                <motion.div
                  key="content"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="space-y-4"
                >
                  {/* Action Buttons */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCopyGuidance}
                      >
                        <Copy className="h-3 w-3 mr-2" />
                        Copy Guidance
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCopyAll}
                      >
                        <BookOpen className="h-3 w-3 mr-2" />
                        Copy All
                      </Button>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleRefresh}
                    >
                      <RefreshCw className="h-3 w-3 mr-2" />
                      Refresh
                    </Button>
                  </div>

                  <Separator />

                  {/* Main Guidance */}
                  <div className="space-y-3">
                    <h4 className="text-sm font-medium flex items-center gap-2">
                      <MessageSquare className="h-4 w-4" />
                      Compliance Guidance
                    </h4>
                    <div className="bg-muted/50 rounded-lg p-4">
                      <ScrollArea className="max-h-40">
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">
                          {aiResponse.guidance}
                        </p>
                      </ScrollArea>
                    </div>
                  </div>

                  {/* Related Topics */}
                  {aiResponse.related_topics && aiResponse.related_topics.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Related Topics</h4>
                      <div className="flex flex-wrap gap-2">
                        {aiResponse.related_topics.map((topic, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Follow-up Suggestions */}
                  {aiResponse.follow_up_suggestions && aiResponse.follow_up_suggestions.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium flex items-center gap-2">
                        <Lightbulb className="h-4 w-4" />
                        Recommended Actions
                      </h4>
                      <div className="space-y-2">
                        {aiResponse.follow_up_suggestions.map((suggestion, index) => (
                          <div key={index} className="flex items-start gap-3 text-sm">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                            <span className="text-muted-foreground">{suggestion}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Source References */}
                  {aiResponse.source_references && aiResponse.source_references.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">References</h4>
                      <div className="space-y-1">
                        {aiResponse.source_references.map((ref, index) => (
                          <div key={index} className="flex items-center gap-2 text-sm text-muted-foreground">
                            <ExternalLink className="h-3 w-3 flex-shrink-0" />
                            <span>{ref}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Separator />

                  {/* Footer */}
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Powered by AI Compliance Assistant</span>
                    <span>Confidence: {Math.round(aiResponse.confidence_score * 100)}%</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
}