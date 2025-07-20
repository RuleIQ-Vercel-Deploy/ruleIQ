"use client"
import { motion, AnimatePresence, useScroll, useMotionValueEvent } from "framer-motion"
import Link from "next/link"
import { useState } from "react"

import { Logo } from "@/components/ui/logo"
import { cn } from "@/lib/utils"


import { Button } from "../button"


import type { JSX } from "react/jsx-runtime" // Import JSX to fix the undeclared variable error

export const FloatingNav = ({
  navItems,
  className,
}: {
  navItems: {
    name: string
    link: string
    icon?: JSX.Element
  }[]
  className?: string
}) => {
  const { scrollYProgress } = useScroll()

  const [visible, setVisible] = useState(true)

  useMotionValueEvent(scrollYProgress, "change", (current) => {
    if (typeof current === "number") {
      const direction = current! - scrollYProgress.getPrevious()!

      if (scrollYProgress.get() < 0.05) {
        setVisible(true)
      } else {
        if (direction < 0) {
          setVisible(true)
        } else {
          setVisible(false)
        }
      }
    }
  })

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{
          opacity: 1,
          y: -100,
        }}
        animate={{
          y: visible ? 0 : -100,
          opacity: visible ? 1 : 0,
        }}
        transition={{
          duration: 0.2,
        }}
        className={cn(
          "flex max-w-fit fixed top-10 inset-x-0 mx-auto border border-white/20 rounded-full bg-midnight-blue/80 backdrop-blur-sm z-50 pr-2 pl-8 py-2 items-center justify-center space-x-4",
          className,
        )}
      >
        <Logo />
        {navItems.map((navItem: any, idx: number) => (
          <Link
            key={`link=${idx}`}
            href={navItem.link}
            className={cn("relative text-eggshell-white items-center flex space-x-1 hover:text-gold transition-colors")}
          >
            <span className="block sm:hidden">{navItem.icon}</span>
            <span className="hidden sm:block text-sm">{navItem.name}</span>
          </Link>
        ))}
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" className="rounded-full bg-transparent">
            Login
          </Button>
          <Button variant="default" size="sm" className="rounded-full">
            Get Started
          </Button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
