"use client"
import { Paperclip } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from "@/components/ui/textarea"


import type { AssessmentQuestion } from "@/lib/data/questionnaire"

interface QuestionCardProps {
  question: AssessmentQuestion
  questionNumber: number
}

export function QuestionCard({ question, questionNumber }: QuestionCardProps) {
  const renderAnswerInput = () => {
    switch (question.type) {
      case "radio":
        return (
          <RadioGroup>
            <div className="space-y-2">
              {question.options?.map((option) => (
                <div key={option} className="flex items-center space-x-2">
                  <RadioGroupItem value={option} id={`${question.id}-${option}`} />
                  <Label htmlFor={`${question.id}-${option}`} className="font-normal">
                    {option}
                  </Label>
                </div>
              ))}
            </div>
          </RadioGroup>
        )
      case "checkbox":
        return (
          <div className="space-y-2">
            {question.options?.map((option) => (
              <div key={option} className="flex items-center space-x-2">
                <Checkbox id={`${question.id}-${option}`} />
                <Label htmlFor={`${question.id}-${option}`} className="font-normal">
                  {option}
                </Label>
              </div>
            ))}
          </div>
        )
      case "textarea":
        return (
          <Textarea
            placeholder={question.placeholder}
            className="bg-muted/20 placeholder:text-muted-foreground border-primary/30 focus:border-primary"
            rows={5}
          />
        )
      default:
        return null
    }
  }

  return (
    <Card
      className="ruleiq-card border-primary/20 bg-card/50 backdrop-blur-sm"
    >
      <CardHeader>
        <CardTitle className="text-lg">
          Question {questionNumber}: {question.text}
        </CardTitle>
        {question.helperText && <CardDescription className="text-muted-foreground pt-1">{question.helperText}</CardDescription>}
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {renderAnswerInput()}
          <div className="flex justify-end pt-2">
            <Button
              variant="outline"
              size="sm"
              className="bg-transparent border-primary/30 hover:bg-primary/10 hover:text-primary"
            >
              <Paperclip className="mr-2 h-4 w-4" />
              Attach Evidence
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
