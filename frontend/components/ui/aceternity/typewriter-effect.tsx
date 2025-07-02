"use client"

import { motion, useInView, AnimatePresence } from "framer-motion"
import { useEffect, useRef, useState } from "react"

import { cn } from "@/lib/utils"

export const TypewriterEffect = ({
  words,
  className,
  cursorClassName,
}: {
  words: {
    text: string
    className?: string
  }[]
  className?: string
  cursorClassName?: string
}) => {
  const [currentWordIndex, setCurrentWordIndex] = useState(0)
  const ref = useRef(null)
  const isInView = useInView(ref)

  useEffect(() => {
    if (!isInView) return
    const interval = setInterval(() => {
      setCurrentWordIndex((prev) => (prev + 1) % words.length)
    }, 2500)

    return () => clearInterval(interval)
  }, [isInView, words.length])

  const currentWord = words[currentWordIndex]
  const wordsArray = currentWord.text.split("")

  const renderWords = () => {
    return (
      <motion.div ref={ref} className="inline">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentWord.text}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {wordsArray.map((char, index) => (
              <motion.span
                key={`char-${index}`}
                className={cn(`text-eggshell-white`, currentWord.className)}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{
                  delay: index * 0.05,
                  duration: 0.1,
                }}
              >
                {char}
              </motion.span>
            ))}
          </motion.div>
        </AnimatePresence>
      </motion.div>
    )
  }

  return (
    <div className={cn("text-base sm:text-xl md:text-3xl lg:text-5xl font-bold text-center", className)}>
      {renderWords()}
      <motion.span
        initial={{
          opacity: 0,
        }}
        animate={{
          opacity: 1,
        }}
        transition={{
          duration: 0.8,
          repeat: Number.POSITIVE_INFINITY,
          repeatType: "reverse",
        }}
        className={cn("inline-block rounded-sm w-[4px] h-4 md:h-6 lg:h-10 bg-gold", cursorClassName)}
      ></motion.span>
    </div>
  )
}
