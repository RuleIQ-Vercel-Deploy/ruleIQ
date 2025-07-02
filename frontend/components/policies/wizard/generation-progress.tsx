"use client"

import { Loader2 } from "lucide-react"
import * as React from "react"

export function GenerationProgress() {
  const [progress, setProgress] = React.useState(0)
  const [estimatedTime, setEstimatedTime] = React.useState(45)

  React.useEffect(() => {
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          return 100
        }
        return prev + 1
      })
    }, 400)

    const timeInterval = setInterval(() => {
      setEstimatedTime((prev) => {
        if (prev <= 0) {
          clearInterval(timeInterval)
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => {
      clearInterval(progressInterval)
      clearInterval(timeInterval)
    }
  }, [])

  return (
    <div className="flex flex-col items-center justify-center text-center h-full space-y-6 p-8 bg-oxford-blue-light rounded-lg border border-white/10">
      <div className="relative">
        <svg className="w-32 h-32 transform -rotate-90">
          <circle
            className="text-gray-700"
            strokeWidth="8"
            stroke="currentColor"
            fill="transparent"
            r="58"
            cx="64"
            cy="64"
          />
          <circle
            className="text-gold"
            strokeWidth="8"
            strokeDasharray={2 * Math.PI * 58}
            strokeDashoffset={2 * Math.PI * 58 - (progress / 100) * (2 * Math.PI * 58)}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r="58"
            cx="64"
            cy="64"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <Loader2 className="w-12 h-12 text-gold animate-spin" />
        </div>
      </div>
      <h2 className="text-2xl font-bold text-eggshell-white">AI is generating your policy...</h2>
      <p className="text-grey-600">This may take a moment. Please don't close this window.</p>
      <div className="w-full bg-gray-700 rounded-full h-2.5">
        <div className="bg-gold h-2.5 rounded-full" style={{ width: `${progress}%` }}></div>
      </div>
      <p className="text-sm text-grey-600">
        Estimated time remaining: <span className="font-semibold text-eggshell-white">{estimatedTime} seconds</span>
      </p>
    </div>
  )
}
