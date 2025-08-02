"use client";

import { format } from "date-fns";
import { 
  Info, 
  Upload, 
  X, 
  FileText,
  Calendar
} from "lucide-react";
import { useState } from "react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { type Question } from "@/lib/assessment-engine/types";
import type { UnknownRecord } from '@/types/common';
import { cn } from "@/lib/utils";
import { type UserContext } from "@/types/ai";

import { InlineAIErrorBoundary } from "./AIErrorBoundary";
import { AIHelpTooltip } from "./AIHelpTooltip";

interface QuestionRendererProps {
  question: Question;
  value: UnknownRecord;
  onChange: (_value: UnknownRecord) => void;
  error?: string | null;
  disabled?: boolean;
  frameworkId?: string;
  sectionId?: string;
  userContext?: UserContext;
}

export function QuestionRenderer({
  question,
  value,
  onChange,
  error,
  disabled = false,
  frameworkId,
  sectionId,
  userContext
}: QuestionRendererProps) {
  const [files, setFiles] = useState<File[]>(value || []);

  const renderQuestion = () => {
    switch (question.type) {
      case 'radio':
        return (
          <RadioGroup
            value={value || ''}
            onValueChange={onChange}
            disabled={disabled}
          >
            <div className="space-y-2">
              {question.options?.map((option) => (
                <div key={option.value} className="flex items-start space-x-2">
                  <RadioGroupItem value={option.value} id={option.value} />
                  <div className="flex-1">
                    <Label 
                      htmlFor={option.value} 
                      className="text-sm font-normal cursor-pointer"
                    >
                      {option.label}
                    </Label>
                    {option.description && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {option.description}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </RadioGroup>
        );

      case 'checkbox': {
        const checkedValues = value || [];
        return (
          <div className="space-y-2">
            {question.options?.map((option) => (
              <div key={option.value} className="flex items-start space-x-2">
                <Checkbox
                  id={option.value}
                  checked={checkedValues.includes(option.value)}
                  onCheckedChange={(checked) => {
                    const newValues = checked
                      ? [...checkedValues, option.value]
                      : checkedValues.filter((v: string) => v !== option.value);
                    onChange(newValues);
                  }}
                  disabled={disabled}
                />
                <div className="flex-1">
                  <Label 
                    htmlFor={option.value} 
                    className="text-sm font-normal cursor-pointer"
                  >
                    {option.label}
                  </Label>
                  {option.description && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {option.description}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        );
      }

      case 'text':
        return (
          <Input
            type="text"
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            placeholder="Enter your answer..."
            className={cn(error && "border-destructive")}
          />
        );

      case 'textarea':
        return (
          <Textarea
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            placeholder="Provide a detailed answer..."
            rows={4}
            className={cn(error && "border-destructive")}
          />
        );

      case 'number':
        return (
          <Input
            type="number"
            value={value || ''}
            onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
            disabled={disabled}
            placeholder="Enter a number..."
            min={question.validation?.min}
            max={question.validation?.max}
            className={cn(error && "border-destructive")}
          />
        );

      case 'date':
        return (
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-full justify-start text-left font-normal",
                  !value && "text-muted-foreground",
                  error && "border-destructive"
                )}
                disabled={disabled}
              >
                <Calendar className="mr-2 h-4 w-4" />
                {value ? format(new Date(value), "PPP") : "Select a date"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <CalendarComponent
                mode="single"
                selected={value ? new Date(value) : undefined}
                onSelect={(date) => onChange(date?.toISOString())}
                disabled={disabled}
                initialFocus
              />
            </PopoverContent>
          </Popover>
        );

      case 'select':
        return (
          <Select
            value={value || ''}
            onValueChange={onChange}
            disabled={disabled}
          >
            <SelectTrigger className={cn(error && "border-destructive")}>
              <SelectValue placeholder="Select an option..." />
            </SelectTrigger>
            <SelectContent>
              {question.options?.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      case 'scale':
        const scaleValue = value || question.scaleMin || 1;
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>{question.scaleLabels?.min || question.scaleMin || 1}</span>
              <span className="text-lg font-semibold text-primary">{scaleValue}</span>
              <span>{question.scaleLabels?.max || question.scaleMax || 5}</span>
            </div>
            <Slider
              value={[scaleValue]}
              onValueChange={([val]) => onChange(val)}
              min={question.scaleMin || 1}
              max={question.scaleMax || 5}
              step={1}
              disabled={disabled}
              className="w-full"
            />
          </div>
        );

      case 'matrix':
        const matrixValue = value || {};
        return (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="text-left p-2 border-b"></th>
                  {question.columns?.map((col) => (
                    <th key={col.id} className="text-center p-2 border-b text-sm">
                      {col.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {question.rows?.map((row) => (
                  <tr key={row.id}>
                    <td className="p-2 border-b text-sm">{row.label}</td>
                    {question.columns?.map((col) => (
                      <td key={col.id} className="text-center p-2 border-b">
                        <RadioGroup
                          value={matrixValue[row.id] || ''}
                          onValueChange={(val) => {
                            onChange({
                              ...matrixValue,
                              [row.id]: val
                            });
                          }}
                          disabled={disabled}
                        >
                          <RadioGroupItem value={col.id} />
                        </RadioGroup>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );

      case 'file_upload':
        return (
          <div className="space-y-4">
            <div className="border-2 border-dashed rounded-lg p-6 text-center">
              <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm text-muted-foreground mb-2">
                Drop files here or click to browse
              </p>
              <Input
                type="file"
                multiple={question.validation?.max !== 1}
                onChange={(e) => {
                  const newFiles = Array.from(e.target.files || []);
                  setFiles(newFiles);
                  onChange(newFiles);
                }}
                disabled={disabled}
                accept={question.metadata?.acceptedTypes?.join(',')}
                className="hidden"
                id={`file-${question.id}`}
              />
              <Label
                htmlFor={`file-${question.id}`}
                className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
              >
                Browse Files
              </Label>
            </div>
            {files.length > 0 && (
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 border rounded">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      <span className="text-sm">{file.name}</span>
                      <span className="text-xs text-muted-foreground">
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        const newFiles = files.filter((_, i) => i !== index);
                        setFiles(newFiles);
                        onChange(newFiles);
                      }}
                      disabled={disabled}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      default:
        return (
          <Alert>
            <AlertDescription>
              Unsupported question type: {question.type}
            </AlertDescription>
          </Alert>
        );
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-start justify-between gap-4 mb-2">
          <h3 className="text-lg font-medium flex-1">
            {question.text}
            {question.validation?.required && (
              <span className="text-destructive ml-1">*</span>
            )}
          </h3>
          {frameworkId && (
            <InlineAIErrorBoundary>
              <AIHelpTooltip
                question={question}
                frameworkId={frameworkId}
                sectionId={sectionId}
                userContext={userContext}
                className="flex-shrink-0"
              />
            </InlineAIErrorBoundary>
          )}
        </div>
        {question.description && (
          <p className="text-sm text-muted-foreground mb-4">
            {question.description}
          </p>
        )}
      </div>

      {renderQuestion()}

      {question.helpText && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription className="text-sm">
            {question.helpText}
          </AlertDescription>
        </Alert>
      )}

      {error && (
        <p className="text-sm text-destructive mt-2">{error}</p>
      )}
    </div>
  );
}