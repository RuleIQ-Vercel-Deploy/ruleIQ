"use client"

import { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { Slider } from "@/components/ui/slider"
import { ChevronLeft, ChevronRight, Save, FileText, HelpCircle, Upload, AlertCircle, CheckCircle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import type { Assessment, AssessmentQuestion, AssessmentAnswer } from "@/types/api"

// Mock data - replace with actual API calls
const mockAssessment: Assessment = {
  id: "1",
  title: "GDPR Compliance Assessment",
  description: "Comprehensive GDPR readiness evaluation",
  framework: "GDPR",
  business_profile_id: "bp1",
  status: "in_progress",
  progress: 65,
  created_at: "2024-01-15T10:00:00Z",
  updated_at: "2024-01-20T14:30:00Z",
  questions_count: 45,
  answered_count: 29,
}

const mockQuestions: AssessmentQuestion[] = [
  {
    id: "q1",
    assessment_id: "1",
    question_text: "Does your organization have a designated Data Protection Officer (DPO)?",
    question_type: "single_choice",
    required: true,
    order: 1,
    section: "Governance",
    control_reference: "GDPR Art. 37",
    weight: 5,
    help_text:
      "A DPO is required for public authorities and organizations that process personal data on a large scale.",
    options: [
      { id: "o1", text: "Yes, we have a designated DPO", value: "yes", score: 5 },
      { id: "o2", text: "No, but we plan to appoint one", value: "planning", score: 2 },
      { id: "o3", text: "No, we don't believe it's required", value: "not_required", score: 3 },
      { id: "o4", text: "No, and we're not sure if it's required", value: "unsure", score: 0 },
    ],
  },
  {
    id: "q2",
    assessment_id: "1",
    question_text: "Describe your current data mapping and inventory processes.",
    question_type: "textarea",
    required: true,
    order: 2,
    section: "Data Management",
    control_reference: "GDPR Art. 30",
    weight: 8,
    help_text:
      "Organizations must maintain records of processing activities including data categories, purposes, and retention periods.",
  },
  {
    id: "q3",
    assessment_id: "1",
    question_text: "Which of the following security measures do you have in place?",
    question_type: "multiple_choice",
    required: true,
    order: 3,
    section: "Security",
    control_reference: "GDPR Art. 32",
    weight: 10,
    options: [
      { id: "o5", text: "Encryption at rest", value: "encryption_rest", score: 3 },
      { id: "o6", text: "Encryption in transit", value: "encryption_transit", score: 3 },
      { id: "o7", text: "Access controls", value: "access_controls", score: 2 },
      { id: "o8", text: "Regular security assessments", value: "security_assessments", score: 2 },
      { id: "o9", text: "Incident response plan", value: "incident_response", score: 2 },
    ],
  },
  {
    id: "q4",
    assessment_id: "1",
    question_text: "Rate your organization's privacy awareness training effectiveness (1-10):",
    question_type: "scale",
    required: true,
    order: 4,
    section: "Training",
    control_reference: "GDPR Art. 39",
    weight: 6,
    help_text: "Consider frequency, content quality, and employee engagement in your rating.",
  },
  {
    id: "q5",
    assessment_id: "1",
    question_text: "Upload your current privacy policy document:",
    question_type: "file_upload",
    required: false,
    order: 5,
    section: "Documentation",
    control_reference: "GDPR Art. 13-14",
    weight: 4,
    help_text: "Privacy policies should be clear, accessible, and regularly updated.",
  },
]

const mockAnswers: AssessmentAnswer[] = [
  {
    id: "a1",
    assessment_id: "1",
    question_id: "q1",
    answer_value: "yes",
    score: 5,
    created_at: "2024-01-15T10:30:00Z",
    updated_at: "2024-01-15T10:30:00Z",
  },
]

interface QuestionRendererProps {
  question: AssessmentQuestion
  answer?: AssessmentAnswer
  onAnswerChange: (questionId: string, value: any, score?: number) => void
}

function QuestionRenderer({ question, answer, onAnswerChange }: QuestionRendererProps) {
  const [localValue, setLocalValue] = useState<any>(answer?.answer_value || "")
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])

  const handleValueChange = (value: any, score?: number) => {
    setLocalValue(value)
    onAnswerChange(question.id, value, score)
  }

  const renderQuestionInput = () => {
    switch (question.question_type) {
      case "single_choice":
        return (
          <RadioGroup
            value={localValue as string}
            onValueChange={(value) => {
              const option = question.options?.find((o) => o.value === value)
              handleValueChange(value, option?.score)
            }}
            className="space-y-3"
          >
            {question.options?.map((option) => (
              <div key={option.id} className="flex items-center space-x-2">
                <RadioGroupItem value={option.value as string} id={option.id} />
                <Label htmlFor={option.id} className="flex-1 cursor-pointer">
                  {option.text}
                </Label>
              </div>
            ))}
          </RadioGroup>
        )

      case "multiple_choice":
        const selectedValues = Array.isArray(localValue) ? localValue : []
        return (
          <div className="space-y-3">
            {question.options?.map((option) => (
              <div key={option.id} className="flex items-center space-x-2">
                <Checkbox
                  id={option.id}
                  checked={selectedValues.includes(option.value)}
                  onCheckedChange={(checked) => {
                    let newValues: any[]
                    if (checked) {
                      newValues = [...selectedValues, option.value]
                    } else {
                      newValues = selectedValues.filter((v: any) => v !== option.value)
                    }
                    const totalScore = newValues.reduce((sum, val) => {
                      const opt = question.options?.find((o) => o.value === val)
                      return sum + (opt?.score || 0)
                    }, 0)
                    handleValueChange(newValues, totalScore)
                  }}
                />
                <Label htmlFor={option.id} className="flex-1 cursor-pointer">
                  {option.text}
                </Label>
              </div>
            ))}
          </div>
        )

      case "text":
        return (
          <Input
            value={localValue as string}
            onChange={(e) => handleValueChange(e.target.value)}
            placeholder="Enter your answer..."
            className="w-full"
          />
        )

      case "textarea":
        return (
          <Textarea
            value={localValue as string}
            onChange={(e) => handleValueChange(e.target.value)}
            placeholder="Provide a detailed answer..."
            className="w-full min-h-[120px]"
          />
        )

      case "boolean":
        return (
          <RadioGroup
            value={localValue as string}
            onValueChange={(value) => handleValueChange(value === "true", value === "true" ? 5 : 0)}
            className="flex space-x-6"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="true" id="yes" />
              <Label htmlFor="yes">Yes</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="false" id="no" />
              <Label htmlFor="no">No</Label>
            </div>
          </RadioGroup>
        )

      case "scale":
        const scaleValue = Array.isArray(localValue) ? localValue[0] : localValue || 5
        return (
          <div className="space-y-4">
            <Slider
              value={[scaleValue]}
              onValueChange={(value) => handleValueChange(value[0], value[0])}
              max={10}
              min={1}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-500">
              <span>1 (Poor)</span>
              <span className="font-medium">Current: {scaleValue}</span>
              <span>10 (Excellent)</span>
            </div>
          </div>
        )

      case "file_upload":
        return (
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="mt-4">
                <Label htmlFor="file-upload" className="cursor-pointer">
                  <span className="mt-2 block text-sm font-medium text-gray-900 dark:text-white">
                    Click to upload files
                  </span>
                  <span className="mt-1 block text-xs text-gray-500">PDF, DOC, DOCX up to 10MB</span>
                </Label>
                <Input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  multiple
                  accept=".pdf,.doc,.docx"
                  onChange={(e) => {
                    const files = Array.from(e.target.files || [])
                    setUploadedFiles(files)
                    handleValueChange(files.map((f) => f.name))
                  }}
                />
              </div>
            </div>
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center space-x-2 text-sm">
                    <FileText className="h-4 w-4" />
                    <span>{file.name}</span>
                    <span className="text-gray-500">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )

      default:
        return <div className="text-gray-500">Unsupported question type</div>
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start space-x-2">
        <div className="flex-1">
          <Label className="text-base font-medium">
            {question.question_text}
            {question.required && <span className="text-red-500 ml-1">*</span>}
          </Label>
          {question.control_reference && (
            <Badge variant="outline" className="ml-2 text-xs">
              {question.control_reference}
            </Badge>
          )}
        </div>
        {question.help_text && (
          <div className="group relative">
            <HelpCircle className="h-4 w-4 text-gray-400 cursor-help" />
            <div className="absolute right-0 top-6 w-64 p-2 bg-black text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity z-10">
              {question.help_text}
            </div>
          </div>
        )}
      </div>
      {renderQuestionInput()}
    </div>
  )
}

export function AssessmentFlow() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { toast } = useToast()

  const [assessment, setAssessment] = useState<Assessment>(mockAssessment)
  const [questions, setQuestions] = useState<AssessmentQuestion[]>(mockQuestions)
  const [answers, setAnswers] = useState<AssessmentAnswer[]>(mockAnswers)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [loading, setLoading] = useState(false)
  const [autoSave, setAutoSave] = useState(true)

  const currentQuestion = questions[currentQuestionIndex]
  const currentAnswer = answers.find((a) => a.question_id === currentQuestion?.id)
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100
  const answeredCount = answers.length
  const isLastQuestion = currentQuestionIndex === questions.length - 1
  const isFirstQuestion = currentQuestionIndex === 0

  const handleAnswerChange = async (questionId: string, value: any, score?: number) => {
    const existingAnswerIndex = answers.findIndex((a) => a.question_id === questionId)
    const newAnswer: AssessmentAnswer = {
      id: existingAnswerIndex >= 0 ? answers[existingAnswerIndex].id : `temp_${Date.now()}`,
      assessment_id: assessment.id,
      question_id: questionId,
      answer_value: value,
      score: score || 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    let newAnswers: AssessmentAnswer[]
    if (existingAnswerIndex >= 0) {
      newAnswers = [...answers]
      newAnswers[existingAnswerIndex] = newAnswer
    } else {
      newAnswers = [...answers, newAnswer]
    }

    setAnswers(newAnswers)

    // Auto-save if enabled
    if (autoSave) {
      try {
        // await assessmentsApi.saveAnswer(assessment.id, questionId, newAnswer)
        toast({
          title: "Answer saved",
          description: "Your response has been automatically saved.",
        })
      } catch (error) {
        toast({
          title: "Save failed",
          description: "Failed to save your answer. Please try again.",
          variant: "destructive",
        })
      }
    }
  }

  const handleNext = () => {
    if (!isLastQuestion) {
      setCurrentQuestionIndex((prev) => prev + 1)
    }
  }

  const handlePrevious = () => {
    if (!isFirstQuestion) {
      setCurrentQuestionIndex((prev) => prev - 1)
    }
  }

  const handleSave = async () => {
    setLoading(true)
    try {
      // Save all answers
      // await Promise.all(answers.map(answer =>
      //   assessmentsApi.saveAnswer(assessment.id, answer.question_id, answer)
      // ))
      toast({
        title: "Assessment saved",
        description: "All your responses have been saved successfully.",
      })
    } catch (error) {
      toast({
        title: "Save failed",
        description: "Failed to save the assessment. Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleComplete = async () => {
    setLoading(true)
    try {
      // Mark assessment as completed and generate results
      // await assessmentsApi.updateAssessment(assessment.id, { status: "completed" })
      // await assessmentsApi.generateResult(assessment.id)
      toast({
        title: "Assessment completed",
        description: "Your assessment has been completed and results are being generated.",
      })
      navigate(`/app/assessments/${assessment.id}/results`)
    } catch (error) {
      toast({
        title: "Completion failed",
        description: "Failed to complete the assessment. Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const getQuestionStatus = (index: number) => {
    const question = questions[index]
    const hasAnswer = answers.some((a) => a.question_id === question.id)
    if (index < currentQuestionIndex) return hasAnswer ? "completed" : "skipped"
    if (index === currentQuestionIndex) return "current"
    return "upcoming"
  }

  if (!currentQuestion) {
    return <div>Loading...</div>
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{assessment.title}</h1>
            <p className="text-gray-600 dark:text-gray-300">{assessment.description}</p>
          </div>
          <Badge variant="outline" className="text-sm">
            {assessment.framework}
          </Badge>
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>
              Question {currentQuestionIndex + 1} of {questions.length}
            </span>
            <span>{answeredCount} answered</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Question Navigation Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Questions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {questions.map((question, index) => {
                const status = getQuestionStatus(index)
                return (
                  <button
                    key={question.id}
                    onClick={() => setCurrentQuestionIndex(index)}
                    className={`w-full text-left p-2 rounded text-sm transition-colors ${
                      status === "current"
                        ? "bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100"
                        : status === "completed"
                          ? "bg-green-100 text-green-900 dark:bg-green-900 dark:text-green-100"
                          : status === "skipped"
                            ? "bg-yellow-100 text-yellow-900 dark:bg-yellow-900 dark:text-yellow-100"
                            : "hover:bg-gray-100 dark:hover:bg-gray-800"
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{index + 1}</span>
                      {status === "completed" && <CheckCircle className="h-3 w-3" />}
                      {status === "skipped" && <AlertCircle className="h-3 w-3" />}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">{question.section}</div>
                  </button>
                )
              })}
            </CardContent>
          </Card>
        </div>

        {/* Main Question Area */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Section: {currentQuestion.section}</CardTitle>
                  <CardDescription>Weight: {currentQuestion.weight} points</CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Label htmlFor="auto-save" className="text-sm">
                    Auto-save
                  </Label>
                  <Checkbox id="auto-save" checked={autoSave} onCheckedChange={setAutoSave} />
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <QuestionRenderer question={currentQuestion} answer={currentAnswer} onAnswerChange={handleAnswerChange} />

              {/* Navigation */}
              <div className="flex items-center justify-between pt-6 border-t">
                <Button variant="outline" onClick={handlePrevious} disabled={isFirstQuestion}>
                  <ChevronLeft className="h-4 w-4 mr-2" />
                  Previous
                </Button>

                <div className="flex space-x-2">
                  <Button variant="outline" onClick={handleSave} disabled={loading}>
                    <Save className="h-4 w-4 mr-2" />
                    Save Progress
                  </Button>

                  {isLastQuestion ? (
                    <Button onClick={handleComplete} disabled={loading} className="bg-green-600 hover:bg-green-700">
                      Complete Assessment
                    </Button>
                  ) : (
                    <Button onClick={handleNext}>
                      Next
                      <ChevronRight className="h-4 w-4 ml-2" />
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
