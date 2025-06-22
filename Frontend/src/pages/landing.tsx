"use client"
import { HeroHighlight, Highlight } from "@/components/aceternity/hero-highlight"
import { TextGenerateEffect } from "@/components/aceternity/text-generate-effect"
import { BentoGrid, BentoGridItem } from "@/components/aceternity/bento-grid"
import { InfiniteMovingCards } from "@/components/aceternity/infinite-moving-cards"
import { BackgroundBeams } from "@/components/aceternity/background-beams"
import { Button } from "@/components/ui/button"
import { Link } from "react-router-dom"
import { Shield, Brain, FileText, BarChart3, Users, Zap } from "lucide-react"

const words = "Automate your compliance journey with AI-powered insights and seamless evidence management."

const testimonials = [
  {
    quote: "NexCompli transformed our GDPR compliance process. What used to take months now takes weeks.",
    name: "Sarah Johnson",
    title: "Compliance Officer at TechCorp",
  },
  {
    quote: "The AI assistant is incredibly helpful for understanding complex compliance requirements.",
    name: "Michael Chen",
    title: "CTO at StartupXYZ",
  },
  {
    quote: "Evidence management has never been easier. Everything is organized and audit-ready.",
    name: "Emma Williams",
    title: "Legal Director at FinanceFlow",
  },
]

const features = [
  {
    title: "AI-Powered Compliance Assistant",
    description: "Get instant answers to compliance questions and personalized recommendations.",
    header: (
      <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-200 dark:from-neutral-900 dark:to-neutral-800 to-neutral-100"></div>
    ),
    icon: <Brain className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "Automated Evidence Collection",
    description: "Streamline evidence gathering with smart automation and integrations.",
    header: (
      <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-200 dark:from-neutral-900 dark:to-neutral-800 to-neutral-100"></div>
    ),
    icon: <FileText className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "Real-time Compliance Scoring",
    description: "Track your compliance readiness with dynamic scoring and gap analysis.",
    header: (
      <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-200 dark:from-neutral-900 dark:to-neutral-800 to-neutral-100"></div>
    ),
    icon: <BarChart3 className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "Multi-Framework Support",
    description: "Support for GDPR, ISO 27001, SOC 2, and more compliance frameworks.",
    header: (
      <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-200 dark:from-neutral-900 dark:to-neutral-800 to-neutral-100"></div>
    ),
    icon: <Shield className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "Team Collaboration",
    description: "Work together with your team on compliance initiatives and evidence review.",
    header: (
      <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-200 dark:from-neutral-900 dark:to-neutral-800 to-neutral-100"></div>
    ),
    icon: <Users className="h-4 w-4 text-neutral-500" />,
  },
  {
    title: "Instant Reports",
    description: "Generate comprehensive compliance reports in seconds, not hours.",
    header: (
      <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-200 dark:from-neutral-900 dark:to-neutral-800 to-neutral-100"></div>
    ),
    icon: <Zap className="h-4 w-4 text-neutral-500" />,
  },
]

export function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-black">
      {/* Hero Section */}
      <HeroHighlight>
        <div className="text-center space-y-8 max-w-4xl mx-auto px-4">
          <h1 className="text-4xl md:text-6xl font-bold text-neutral-700 dark:text-white max-w-4xl leading-relaxed lg:leading-snug mx-auto">
            Simplify Compliance with <Highlight className="text-black dark:text-white">AI-Powered Automation</Highlight>
          </h1>

          <TextGenerateEffect
            words={words}
            className="text-lg md:text-xl text-neutral-600 dark:text-neutral-300 max-w-2xl mx-auto"
          />

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-8">
            <Button asChild size="lg" className="px-8 py-3">
              <Link to="/register">Get Started Free</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="px-8 py-3">
              <Link to="/login">Sign In</Link>
            </Button>
          </div>
        </div>
      </HeroHighlight>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-800 dark:text-neutral-200 mb-4">
              Everything you need for compliance
            </h2>
            <p className="text-lg text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto">
              From evidence collection to audit readiness, NexCompli provides all the tools you need to stay compliant.
            </p>
          </div>

          <BentoGrid className="max-w-4xl mx-auto">
            {features.map((item, i) => (
              <BentoGridItem
                key={i}
                title={item.title}
                description={item.description}
                header={item.header}
                icon={item.icon}
                className={i === 3 || i === 6 ? "md:col-span-2" : ""}
              />
            ))}
          </BentoGrid>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 px-4 bg-neutral-50 dark:bg-neutral-900">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-800 dark:text-neutral-200 mb-4">
              Trusted by compliance teams worldwide
            </h2>
            <p className="text-lg text-neutral-600 dark:text-neutral-400">
              See what our customers are saying about NexCompli
            </p>
          </div>

          <InfiniteMovingCards items={testimonials} direction="right" speed="slow" />
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <BackgroundBeams />
        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-neutral-800 dark:text-neutral-200 mb-6">
            Ready to transform your compliance process?
          </h2>
          <p className="text-lg text-neutral-600 dark:text-neutral-400 mb-8 max-w-2xl mx-auto">
            Join thousands of companies who trust NexCompli to streamline their compliance operations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="px-8 py-3">
              <Link to="/register">Start Free Trial</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="px-8 py-3">
              <Link to="/contact">Schedule Demo</Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}
