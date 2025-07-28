'use client';

import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot,
  ChevronDown,
  ChevronUp,
  Copy,
  MessageSquare,
  Lightbulb,
  BookOpen,
  ExternalLink,
  RefreshCw,
} from 'lucide-react';
import React, { useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { assessmentAIService, type AIHelpResponse } from '@/lib/api/assessments-ai.service';
import { type Question } from '@/lib/assessment-engine/types';
import { cn } from '@/lib/utils';
import { type UserContext } from '@/types/ai';

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
  defaultOpen = false,
}: AIGuidancePanelProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState<AIHelpResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);
  const { toast } = useToast();

  // Suppress TypeScript unused variable warning
  void requestId;

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
      const helpRequest = {
        question_id: question.id,
        question_text: question.text,
        framework_id: frameworkId,
        ...(sectionId && { section_id: sectionId }),
        ...(userContext && { user_context: userContext }),
      };

      const response = await assessmentAIService.getQuestionHelp(helpRequest);

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
        title: 'Guidance copied',
        description: 'AI guidance has been copied to your clipboard.',
        duration: 2000,
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
      ...(aiResponse.follow_up_suggestions
        ? ['Suggestions:', ...aiResponse.follow_up_suggestions.map((s) => `• ${s}`), '']
        : []),
      ...(aiResponse.source_references
        ? ['References:', ...aiResponse.source_references.map((ref) => `• ${ref}`)]
        : []),
    ].join('\n');

    navigator.clipboard.writeText(fullContent);
    toast({
      title: 'Full guidance copied',
      description: 'Complete AI guidance has been copied to your clipboard.',
      duration: 2000,
    });
  };

  return (
    <Card className={cn('border-l-4 border-l-primary', className)}>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <CardHeader
            className="cursor-pointer transition-colors hover:bg-muted/50"
            onClick={handleToggle}
          >
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Bot className="h-4 w-4 text-primary" />
                AI Compliance Guidance
                {aiResponse && (
                  <Badge variant="outline" className="text-xs">
                    {Math.round(aiResponse.confidence_score * 100)}% confidence
                  </Badge>
                )}
              </CardTitle>
              <div className="p-1" onClick={(e) => e.stopPropagation()}>
                {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
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
                  className="py-8 text-center"
                >
                  <Bot className="mx-auto mb-3 h-8 w-8 animate-pulse text-primary" />
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
                  className="py-6 text-center"
                >
                  <p className="mb-3 text-sm text-destructive">{error}</p>
                  <Button variant="outline" size="sm" onClick={loadGuidance}>
                    <RefreshCw className="mr-2 h-4 w-4" />
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
                      <Button variant="outline" size="sm" onClick={handleCopyGuidance}>
                        <Copy className="mr-2 h-3 w-3" />
                        Copy Guidance
                      </Button>
                      <Button variant="outline" size="sm" onClick={handleCopyAll}>
                        <BookOpen className="mr-2 h-3 w-3" />
                        Copy All
                      </Button>
                    </div>
                    <Button variant="ghost" size="sm" onClick={handleRefresh}>
                      <RefreshCw className="mr-2 h-3 w-3" />
                      Refresh
                    </Button>
                  </div>

                  <Separator />

                  {/* Main Guidance */}
                  <div className="space-y-3">
                    <h4 className="flex items-center gap-2 text-sm font-medium">
                      <MessageSquare className="h-4 w-4" />
                      Compliance Guidance
                    </h4>
                    <div className="rounded-lg bg-muted/50 p-4">
                      <ScrollArea className="max-h-40">
                        <p className="whitespace-pre-wrap text-sm leading-relaxed">
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
                          <Badge key={`topic-${index}-${topic.substring(0, 20)}`} variant="secondary" className="text-xs">
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Follow-up Suggestions */}
                  {aiResponse.follow_up_suggestions &&
                    aiResponse.follow_up_suggestions.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="flex items-center gap-2 text-sm font-medium">
                          <Lightbulb className="h-4 w-4" />
                          Recommended Actions
                        </h4>
                        <div className="space-y-2">
                          {aiResponse.follow_up_suggestions.map((suggestion, index) => (
                            <div key={`suggestion-${index}-${suggestion.substring(0, 25)}`} className="flex items-start gap-3 text-sm">
                              <div className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-primary" />
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
                          <div
                            key={`reference-${index}-${ref.substring(0, 25)}`}
                            className="flex items-center gap-2 text-sm text-muted-foreground"
                          >
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
