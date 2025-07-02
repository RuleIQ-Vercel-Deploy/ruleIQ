"use client"

import { ChevronLeft, ChevronRight, Save } from "lucide-react"
import Link from "next/link"
import * as React from "react"

import { AutoSaveIndicator } from "@/components/assessments/questionnaire/auto-save-indicator"
import { QuestionCard } from "@/components/assessments/questionnaire/question-card"
import { Button } from "@/components/ui/button"
import { ProgressBar } from "@/components/ui/progress-bar"
import { assessmentData } from "@/lib/data/questionnaire"
import { cn } from "@/lib/utils"

export default function AssessmentPage({ params }: { params: { id: string } }) {
  const [currentSectionIndex, setCurrentSectionIndex] = React.useState(0)
  const { title, sections } = assessmentData
  const currentSection = sections[currentSectionIndex]

  const totalProgress = sections.reduce((acc, section) => acc + section.progress, 0) / sections.length

  const handleNext = () => {
    if (currentSectionIndex < sections.length - 1) {
      setCurrentSectionIndex(currentSectionIndex + 1)
    }
  }

  const handleBack = () => {
    if (currentSectionIndex > 0) {
      setCurrentSectionIndex(currentSectionIndex - 1)
    }
  }

  return (
    <div
      className="min-h-screen w-full"
      style={{
        backgroundColor: "#002147",
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fillRule='evenodd'%3E%3Cg fill='%23F0EAD6' fillOpacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      }}
    >
      {/* Header */}
      <header className="sticky top-0 z-40 w-full border-b border-gold/20 bg-oxford-blue/80 backdrop-blur-lg">
        <div className="container mx-auto flex h-16 max-w-screen-2xl items-center justify-between px-6">
          <div className="flex-1">
            <h1 className="text-lg font-semibold text-eggshell-white truncate">{title}</h1>
            <p className="text-sm text-grey-600">Assessment ID: {params.id}</p>
          </div>
          <div className="flex-1 flex justify-end">
            <AutoSaveIndicator />
          </div>
        </div>
        {/* Overall Progress Bar */}
        <div>
          <ProgressBar value={totalProgress} color="warning" className="h-1 bg-gold/20" />
        </div>
      </header>

      <div className="container mx-auto max-w-screen-2xl px-6 py-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
          {/* Left Sidebar for Section Navigation */}
          <aside className="lg:col-span-3 lg:sticky lg:top-24 self-start">
            <nav className="space-y-1">
              {sections.map((section, index) => (
                <button
                  key={section.id}
                  onClick={() => setCurrentSectionIndex(index)}
                  className={cn(
                    "w-full text-left px-4 py-3 rounded-lg transition-colors duration-200 flex items-center justify-between",
                    currentSectionIndex === index ? "bg-gold/10 text-gold" : "text-eggshell-white hover:bg-white/10",
                  )}
                >
                  <div className="flex-1">
                    <p className="font-medium">{section.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <ProgressBar value={section.progress} className="h-1 bg-white/20" color="warning" />
                      <span className="text-xs text-grey-600">{section.progress}%</span>
                    </div>
                  </div>
                  {currentSectionIndex === index && <ChevronRight className="h-5 w-5 text-gold" />}
                </button>
              ))}
            </nav>
          </aside>

          {/* Main Content Area for Questions */}
          <main className="lg:col-span-9">
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-eggshell-white">{currentSection.title}</h2>
              {currentSection.questions.map((question, index) => (
                <QuestionCard key={question.id} question={question} questionNumber={index + 1} />
              ))}

              {/* Bottom Navigation */}
              <div className="flex items-center justify-between pt-6">
                <Button
                  variant="outline"
                  size="medium"
                  className="bg-transparent border-gold/30 text-eggshell-white hover:bg-gold/10 hover:text-gold"
                  onClick={handleBack}
                  disabled={currentSectionIndex === 0}
                >
                  <ChevronLeft className="mr-2 h-4 w-4" />
                  Previous
                </Button>
                <Link href="/assessments" passHref>
                  <Button variant="ghost" className="text-eggshell-white hover:bg-white/10 hover:text-eggshell-white">
                    <Save className="mr-2 h-4 w-4" />
                    Save & Exit
                  </Button>
                </Link>
                <Button
                  variant="accent"
                  size="medium"
                  onClick={handleNext}
                  disabled={currentSectionIndex === sections.length - 1}
                >
                  Next
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
