"use client";

import { 
  CheckCircle2, 
  Circle, 
  Clock,
  Users,
  Calendar,
  AlertTriangle,
  ChevronDown,
  ChevronRight
} from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { 
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger 
} from "@/components/ui/collapsible";
import { type Recommendation, type Gap } from "@/lib/assessment-engine/types";
import { cn } from "@/lib/utils";


interface ActionItemsListProps {
  recommendations: Recommendation[];
  gaps: Gap[];
}

interface ActionItem {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  timeline: string;
  resources: string[];
  relatedGaps: string[];
  completed: boolean;
  subtasks?: {
    id: string;
    title: string;
    completed: boolean;
  }[];
}

export function ActionItemsList({ recommendations, gaps }: ActionItemsListProps) {
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  const [completedItems, setCompletedItems] = useState<Set<string>>(new Set());

  // Convert recommendations to action items
  const actionItems: ActionItem[] = recommendations.map(rec => ({
    id: rec.id,
    title: rec.title,
    description: rec.description,
    priority: rec.priority,
    timeline: rec.estimatedTime,
    resources: rec.resources,
    relatedGaps: rec.relatedGaps || [],
    completed: false,
    subtasks: [
      { id: `${rec.id}-1`, title: 'Assign responsible team members', completed: false },
      { id: `${rec.id}-2`, title: 'Define success criteria', completed: false },
      { id: `${rec.id}-3`, title: 'Create implementation plan', completed: false },
      { id: `${rec.id}-4`, title: 'Execute and monitor progress', completed: false },
      { id: `${rec.id}-5`, title: 'Verify completion and effectiveness', completed: false }
    ]
  }));

  // Sort by priority
  const sortedItems = [...actionItems].sort((a, b) => {
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    return priorityOrder[a.priority] - priorityOrder[b.priority];
  });

  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const toggleCompleted = (itemId: string) => {
    setCompletedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'medium':
        return <Circle className="h-4 w-4 text-yellow-600" />;
      default:
        return <Circle className="h-4 w-4 text-green-600" />;
    }
  };

  const completedCount = completedItems.size;
  const totalCount = sortedItems.length;
  const progressPercentage = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  return (
    <div className="space-y-4">
      {/* Progress Summary */}
      <div className="bg-muted/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-sm font-medium">Overall Progress</h4>
          <span className="text-sm text-muted-foreground">
            {completedCount} of {totalCount} completed
          </span>
        </div>
        <div className="w-full bg-muted rounded-full h-2">
          <div 
            className="bg-gold h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Action Items */}
      <div className="space-y-3">
        {sortedItems.map((item) => {
          const isExpanded = expandedItems.includes(item.id);
          const isCompleted = completedItems.has(item.id);
          
          return (
            <Collapsible
              key={item.id}
              open={isExpanded}
              onOpenChange={() => toggleExpanded(item.id)}
            >
              <div className={cn(
                "border rounded-lg transition-all",
                isCompleted && "opacity-60 bg-muted/30"
              )}>
                <div className="p-4">
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={isCompleted}
                      onCheckedChange={() => toggleCompleted(item.id)}
                      className="mt-1"
                    />
                    <div className="flex-1 space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <h4 className={cn(
                            "font-medium leading-tight",
                            isCompleted && "line-through"
                          )}>
                            {item.title}
                          </h4>
                          <p className="text-sm text-muted-foreground mt-1">
                            {item.description}
                          </p>
                        </div>
                        <CollapsibleTrigger asChild>
                          <Button variant="ghost" size="sm">
                            {isExpanded ? (
                              <ChevronDown className="h-4 w-4" />
                            ) : (
                              <ChevronRight className="h-4 w-4" />
                            )}
                          </Button>
                        </CollapsibleTrigger>
                      </div>
                      
                      {/* Metadata */}
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1">
                          {getPriorityIcon(item.priority)}
                          <span className="capitalize">{item.priority}</span>
                        </div>
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Clock className="h-4 w-4" />
                          <span>{item.timeline}</span>
                        </div>
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Users className="h-4 w-4" />
                          <span>{item.resources.length} teams</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <CollapsibleContent>
                  <div className="px-4 pb-4 space-y-3">
                    <div className="pl-9 space-y-3">
                      {/* Subtasks */}
                      <div>
                        <h5 className="text-sm font-medium mb-2">Implementation Steps</h5>
                        <div className="space-y-2">
                          {item.subtasks?.map((subtask) => (
                            <div key={subtask.id} className="flex items-center gap-2">
                              <Checkbox
                                checked={subtask.completed || isCompleted}
                                disabled={isCompleted}
                                className="h-3 w-3"
                              />
                              <span className={cn(
                                "text-sm",
                                (subtask.completed || isCompleted) && "line-through text-muted-foreground"
                              )}>
                                {subtask.title}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      {/* Resources */}
                      <div>
                        <h5 className="text-sm font-medium mb-2">Required Resources</h5>
                        <div className="flex flex-wrap gap-2">
                          {item.resources.map((resource) => (
                            <Badge key={resource} variant="secondary" className="text-xs">
                              {resource}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      {/* Related Gaps */}
                      {item.relatedGaps.length > 0 && (
                        <div>
                          <h5 className="text-sm font-medium mb-2">Addresses Gaps</h5>
                          <div className="space-y-1">
                            {item.relatedGaps.map((gapId) => {
                              const gap = gaps.find(g => g.questionId === gapId);
                              if (!gap) return null;
                              return (
                                <div key={gapId} className="text-sm text-muted-foreground">
                                  • {gap.questionText}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                      
                      {/* Actions */}
                      <div className="flex items-center gap-2 pt-2">
                        <Button size="sm" variant="outline">
                          <Calendar className="h-3 w-3 mr-2" />
                          Schedule
                        </Button>
                        <Button size="sm" variant="outline">
                          <Users className="h-3 w-3 mr-2" />
                          Assign Team
                        </Button>
                      </div>
                    </div>
                  </div>
                </CollapsibleContent>
              </div>
            </Collapsible>
          );
        })}
      </div>

      {/* Export Actions */}
      <div className="flex items-center justify-center gap-2 pt-4 border-t">
        <Button variant="outline" size="sm">
          Export to Project Management
        </Button>
        <Button variant="outline" size="sm">
          Generate PDF Report
        </Button>
      </div>
    </div>
  );
}