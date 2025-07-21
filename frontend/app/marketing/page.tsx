'use client';
import { motion } from 'framer-motion';
import { ShieldCheck, FileText, BrainCircuit, CheckCircle, BarChart, Users } from 'lucide-react';
import Image from 'next/image';

import { BackgroundGradient } from '@/components/ui/aceternity/background-gradient';
import { CardSpotlight } from '@/components/ui/aceternity/card-spotlight';
import { ContainerScroll } from '@/components/ui/aceternity/container-scroll-animation';
import { FloatingNav } from '@/components/ui/aceternity/floating-nav';
import { HoverEffect } from '@/components/ui/aceternity/hover-effect';
import { InfiniteMovingCards } from '@/components/ui/aceternity/infinite-moving-cards';
import { LampContainer } from '@/components/ui/aceternity/lamp';
import { SparklesCore } from '@/components/ui/aceternity/sparkles';
import { TextGenerateEffect } from '@/components/ui/aceternity/text-generate-effect';
import { TypewriterEffect } from '@/components/ui/aceternity/typewriter-effect';
import { WavyBackground } from '@/components/ui/aceternity/wavy-background';
import { BeamsBackground } from '@/components/ui/beams-background';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Logo } from '@/components/ui/logo';

export default function MarketingPage() {
  const navItems = [
    { name: 'Features', link: '#features' },
    { name: 'Pricing', link: '#pricing' },
    { name: 'About', link: '#about' },
    { name: 'Blog', link: '#blog' },
  ];

  const typewriterWords = [
    { text: 'For UK SMBs', className: 'text-gold' },
    { text: 'AI-Powered', className: 'text-gold' },
    { text: 'Stay Compliant', className: 'text-gold' },
  ];

  const clientLogos = [
    {
      quote: 'Trusted Partner',
      name: 'Client 1',
      title: 'UK Enterprise',
      img: '/placeholder.svg?width=150&height=40',
    },
    {
      quote: 'Trusted Partner',
      name: 'Client 2',
      title: 'UK Enterprise',
      img: '/placeholder.svg?width=150&height=40',
    },
    {
      quote: 'Trusted Partner',
      name: 'Client 3',
      title: 'UK Enterprise',
      img: '/placeholder.svg?width=150&height=40',
    },
    {
      quote: 'Trusted Partner',
      name: 'Client 4',
      title: 'UK Enterprise',
      img: '/placeholder.svg?width=150&height=40',
    },
    {
      quote: 'Trusted Partner',
      name: 'Client 5',
      title: 'UK Enterprise',
      img: '/placeholder.svg?width=150&height=40',
    },
  ];

  const features = [
    {
      icon: <BrainCircuit size={48} className="text-gold" />,
      title: 'AI-Powered Assessments',
      description:
        'Leverage artificial intelligence to conduct comprehensive compliance assessments, identifying gaps and risks with unparalleled accuracy.',
    },
    {
      icon: <FileText size={48} className="text-gold" />,
      title: 'Evidence Management',
      description:
        'A centralized, secure repository for all your compliance evidence. Link documents to controls and automate collection.',
    },
    {
      icon: <ShieldCheck size={48} className="text-gold" />,
      title: 'Policy Generation',
      description:
        'Automatically generate, customize, and manage compliance policies based on industry standards and your specific business needs.',
    },
  ];

  const howItWorksItems = [
    {
      title: 'Connect Your Systems',
      description:
        'Integrate seamlessly with your existing tools and platforms. ruleIQ pulls data from your cloud services, code repositories, and HR systems.',
      link: '#',
      icon: <Users size={32} />,
    },
    {
      title: 'AI Analyzes Compliance',
      description:
        'Our intelligent engine analyzes your data against hundreds of controls from various frameworks like ISO 27001, GDPR, and SOC 2.',
      link: '#',
      icon: <BarChart size={32} />,
    },
    {
      title: 'Get Actionable Insights',
      description:
        'Receive a clear, prioritized list of actions. The dashboard visualizes your compliance posture, making it easy to track progress and report to stakeholders.',
      link: '#',
      icon: <CheckCircle size={32} />,
    },
  ];

  const testimonials = [
    {
      quote:
        "ruleIQ transformed our compliance process from a quarterly headache to a continuous, automated workflow. We're more secure and saved hundreds of hours.",
      name: 'Jane Doe',
      title: 'CTO, TechCorp',
      img: '/placeholder.svg?width=80&height=80',
    },
    {
      quote:
        'The AI-powered insights are a game-changer. We identified critical risks we would have otherwise missed. Highly recommended for any growing business in the UK.',
      name: 'John Smith',
      title: 'CEO, Innovate Solutions',
      img: '/placeholder.svg?width=80&height=80',
    },
  ];

  return (
    <div className="bg-midnight-blue text-eggshell-white relative min-h-screen overflow-x-hidden">
      <FloatingNav navItems={navItems} />

      {/* Hero Section */}
      <section className="relative h-screen w-full">
        <BeamsBackground intensity="strong" className="absolute inset-0 z-0" />
        <div className="bg-midnight-blue/85 absolute inset-0 z-10" />
        <div className="relative z-20 flex h-full flex-col items-center justify-center px-4">
          <div className="space-y-8 text-center">
            <TextGenerateEffect
              words="Automate Compliance, Eliminate Risk"
              className="text-4xl font-bold md:text-6xl lg:text-7xl"
            />
            <TypewriterEffect words={typewriterWords} />
            <div className="relative flex items-center justify-center space-x-4">
              <SparklesCore
                id="hero-sparkles"
                background="transparent"
                minSize={0.6}
                maxSize={1.4}
                particleDensity={100}
                className="absolute h-full w-full"
                particleColor="#FFD700"
              />
              <Button variant="default" size="lg" className="z-10">
                Start Free Trial
              </Button>
              <Button variant="outline" size="lg" className="z-10 bg-transparent">
                Watch Demo
              </Button>
            </div>
          </div>
          <div className="absolute bottom-10 flex space-x-8">
            {['ISO 27001', 'GDPR', 'SOC 2'].map((badge, i) => (
              <motion.div
                key={badge}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: [0, -10, 0] }}
                transition={{
                  duration: 0.5,
                  delay: 1 + i * 0.2,
                  repeat: Number.POSITIVE_INFINITY,
                  repeatType: 'mirror',
                  ease: 'easeInOut',
                }}
                className="flex items-center gap-2 rounded-full border border-gold/30 bg-white/5 px-4 py-2 text-sm"
              >
                <CheckCircle className="text-green-success h-4 w-4" />
                {badge}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof Section */}
      <section className="py-20">
        <BackgroundGradient containerClassName="max-w-5xl mx-auto rounded-[22px]">
          <div className="bg-midnight-blue/90 rounded-[22px] p-8">
            <h3 className="text-eggshell-white mb-8 text-center text-2xl font-semibold">
              Trusted by 500+ UK businesses
            </h3>
            <InfiniteMovingCards items={clientLogos} direction="right" speed="slow" />
          </div>
        </BackgroundGradient>
      </section>

      {/* Features Section */}
      <section id="features" className="px-4 py-20">
        <h2 className="mb-12 text-center text-4xl font-bold md:text-5xl">
          Everything you need. Nothing you don't.
        </h2>
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 md:grid-cols-3">
          {features.map((feature, i) => (
            <CardSpotlight key={i}>
              <div className="text-center">
                {feature.icon}
                <h3 className="text-eggshell-white mt-4 text-2xl font-bold">{feature.title}</h3>
                <p className="text-eggshell-white/80 mt-2">{feature.description}</p>
              </div>
            </CardSpotlight>
          ))}
        </div>
      </section>

      {/* Product Demo Section */}
      <section>
        <ContainerScroll
          titleComponent={
            <h2 className="text-eggshell-white text-4xl font-semibold">
              Your Compliance Command Center <br />
              <span className="mt-1 text-4xl font-bold leading-none text-gold md:text-[6rem]">
                One Dashboard
              </span>
            </h2>
          }
        >
          <Image
            src={`/placeholder.svg?width=1200&height=800&query=modern+dark+theme+compliance+dashboard+UI`}
            alt="Product demo"
            height={800}
            width={1200}
            className="mx-auto h-full rounded-2xl object-cover object-left-top"
            draggable={false}
          />
        </ContainerScroll>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works">
        <LampContainer>
          <motion.h1
            initial={{ opacity: 0.5, y: 100 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{
              delay: 0.3,
              duration: 0.8,
              ease: 'easeInOut',
            }}
            className="from-eggshell-white to-eggshell-white/50 bg-gradient-to-br bg-clip-text py-4 text-center text-4xl font-medium tracking-tight text-transparent md:text-7xl"
          >
            Simple Steps to Full Compliance
          </motion.h1>
        </LampContainer>
        <div className="bg-midnight-blue -mt-48">
          <HoverEffect items={howItWorksItems} />
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="relative">
        <WavyBackground className="mx-auto max-w-4xl pb-40">
          <h2 className="inter-var text-center text-2xl font-bold text-white md:text-4xl lg:text-7xl">
            Don't just take our word for it.
          </h2>
          <p className="inter-var mt-4 text-center text-base font-normal text-white md:text-lg">
            Hear from leaders who transformed their compliance with ruleIQ.
          </p>
          <div className="mt-12 grid grid-cols-1 gap-8 md:grid-cols-2">
            {testimonials.map((t, i) => (
              <BackgroundGradient key={i} containerClassName="rounded-2xl">
                <div className="bg-midnight-blue/80 space-y-4 rounded-2xl p-8 backdrop-blur-sm">
                  <p className="text-lg">"{t.quote}"</p>
                  <div className="flex items-center gap-4">
                    <Image
                      src={t.img || '/placeholder.svg'}
                      alt={t.name}
                      width={40}
                      height={40}
                      className="rounded-full"
                    />
                    <div>
                      <p className="font-semibold">{t.name}</p>
                      <p className="text-eggshell-white/70 text-sm">{t.title}</p>
                    </div>
                  </div>
                </div>
              </BackgroundGradient>
            ))}
          </div>
        </WavyBackground>
      </section>

      {/* CTA Section */}
      <section className="from-midnight-blue bg-gradient-to-b to-[#10162c] py-20">
        <div className="mx-auto max-w-3xl text-center">
          <TextGenerateEffect
            words="Ready to Automate Your Compliance?"
            className="text-4xl font-bold md:text-5xl"
          />
          <p className="text-eggshell-white/80 mt-4">
            Join hundreds of UK businesses securing their operations with ruleIQ. Get started today.
          </p>
          <div className="mx-auto mt-8 max-w-md">
            <div className="flex flex-col gap-4 sm:flex-row">
              <Input
                type="email"
                placeholder="Enter your email"
                className="bg-midnight-blue/50 border-gold/30 focus:border-gold focus:ring-gold"
              />
              <Button variant="default" className="w-full sm:w-auto">
                Get Started Free
              </Button>
            </div>
            <p className="text-eggshell-white/60 mt-2 text-xs">No credit card required.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-eggshell-white/70 bg-[#10162c] px-4 py-12">
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 md:grid-cols-4">
          <div className="space-y-4">
            <Logo />
            <p className="text-sm">Automated compliance for the modern business.</p>
          </div>
          <div>
            <h4 className="text-eggshell-white mb-4 font-semibold">Product</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#features" className="hover:text-gold">
                  Features
                </a>
              </li>
              <li>
                <a href="#pricing" className="hover:text-gold">
                  Pricing
                </a>
              </li>
              <li>
                <a href="#integrations" className="hover:text-gold">
                  Integrations
                </a>
              </li>
              <li>
                <a href="#demo" className="hover:text-gold">
                  Request a Demo
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="text-eggshell-white mb-4 font-semibold">Company</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#about" className="hover:text-gold">
                  About Us
                </a>
              </li>
              <li>
                <a href="#blog" className="hover:text-gold">
                  Blog
                </a>
              </li>
              <li>
                <a href="#careers" className="hover:text-gold">
                  Careers
                </a>
              </li>
              <li>
                <a href="#contact" className="hover:text-gold">
                  Contact
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="text-eggshell-white mb-4 font-semibold">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#privacy" className="hover:text-gold">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#terms" className="hover:text-gold">
                  Terms of Service
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-12 border-t border-white/10 pt-8 text-center text-sm">
          <p>&copy; {new Date().getFullYear()} ruleIQ. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
