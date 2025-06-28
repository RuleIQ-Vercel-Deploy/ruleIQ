"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store/auth-store";
import { motion } from "motion/react";
import RuleIQHeader from "@/components/ruleiq-header";
import { RuleIQLogo } from "@/components/ruleiq-logo";
import {
  Shield,
  FileCheck,
  Users,
  WandSparkles,
  Gauge,
  Mail,
  MapPin,
  MousePointerClick,
  TrendingUpIcon,
} from "lucide-react";
import { HoverBorderGradient } from "@/components/hover-border-gradient";
import { AuroraBackground } from "@/components/ui/aurora-background";
import { PricingSection } from "@/components/payment/pricing-card";


// Benefit Card Component
interface BenefitCardProps {
  title: string;
  description: string;
  stats: string;
}

const BenefitCard = ({ title, description, stats }: BenefitCardProps) => {
  return (
    <div className="bg-gradient-to-br from-[#1a1d29] to-[#0f1117] p-8 rounded-2xl border border-[#2a2d3a] hover:border-[#3a3d4a] transition-all duration-300 hover:transform hover:scale-105">
      <h3 className="text-2xl font-semibold text-white mb-4">{title}</h3>
      <p className="text-gray-300 text-sm leading-relaxed mb-4">{description}</p>
      <div className="text-[#8096D2] font-medium text-sm">{stats}</div>
    </div>
  );
};

// Testimonial Card Component
interface TestimonialCardProps {
  quote: string;
  author: string;
  title: string;
  company: string;
  rating: number;
}

const TestimonialCard = ({ quote, author, title, company, rating }: TestimonialCardProps) => {
  return (
    <div className="bg-gradient-to-br from-[#1a1d29] to-[#0f1117] p-6 rounded-2xl border border-[#2a2d3a] hover:border-[#3a3d4a] transition-all duration-300">
      <div className="flex mb-4">
        {[...Array(rating)].map((_, i) => (
          <span key={i} className="text-yellow-400 text-lg">★</span>
        ))}
      </div>
      <p className="text-gray-300 text-sm leading-relaxed mb-6 italic">"{quote}"</p>
      <div className="border-t border-[#2a2d3a] pt-4">
        <p className="text-white font-semibold">{author}</p>
        <p className="text-[#8096D2] text-sm">{title}</p>
        <p className="text-gray-400 text-xs">{company}</p>
      </div>
    </div>
  );
};

// Pricing Card Component
interface PricingCardProps {
  title: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  buttonText: string;
  popular: boolean;
}

const PricingCard = ({ title, price, period, description, features, buttonText, popular }: PricingCardProps) => {
  return (
    <div className={`relative bg-gradient-to-br from-[#1a1d29] to-[#0f1117] p-8 rounded-2xl border transition-all duration-300 hover:transform hover:scale-105 ${
      popular
        ? 'border-[#8096D2] shadow-lg shadow-[#8096D2]/20'
        : 'border-[#2a2d3a] hover:border-[#3a3d4a]'
    }`}>
      {popular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <span className="bg-gradient-to-r from-[#8096D2] to-[#5B698B] text-white px-4 py-1 rounded-full text-sm font-medium">
            Most Popular
          </span>
        </div>
      )}

      <div className="text-center mb-6">
        <h3 className="text-2xl font-bold text-white mb-2">{title}</h3>
        <div className="mb-2">
          <span className="text-4xl font-bold text-white">{price}</span>
          {price !== "Custom" && <span className="text-gray-400 text-lg">/{period}</span>}
        </div>
        <p className="text-gray-300 text-sm">{description}</p>
      </div>

      <ul className="space-y-3 mb-8">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center text-gray-300 text-sm">
            <span className="text-[#8096D2] mr-3">✓</span>
            {feature}
          </li>
        ))}
      </ul>

      <button className={`w-full py-3 px-6 rounded-lg font-medium transition-all duration-300 ${
        popular
          ? 'bg-gradient-to-r from-[#8096D2] to-[#5B698B] text-white hover:shadow-lg hover:shadow-[#8096D2]/30'
          : 'bg-transparent border border-[#8096D2] text-[#8096D2] hover:bg-[#8096D2] hover:text-white'
      }`}>
        {buttonText}
      </button>
    </div>
  );
};

// Feature Card Component
interface FeatureCardProps {
  title: string;
  text: string;
  icon: React.ReactNode;
}

const FeatureCard = ({ title, text, icon }: FeatureCardProps) => {
  return (
    <div className="flex flex-col items-center text-center p-8 hover:bg-white/5 rounded-lg transition-colors">
      <div className="text-[#8096D2] mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-white mb-4">
        {title}
      </h3>
      <p className="text-gray-300 text-sm leading-relaxed">
        {text}
      </p>
    </div>
  );
};

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered1, setIsHovered1] = useState(false);
  const [isHovered2, setIsHovered2] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [mounted, isAuthenticated, router]);

  const handleMouseMove = (event: React.MouseEvent<HTMLButtonElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setMousePosition({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    });
  };

  return (
    <div className="relative min-h-screen w-full h-full overflow-hidden">
      <AuroraBackground className="dark:bg-zinc-900 min-h-screen h-auto w-full">
        <RuleIQHeader />

        <main className="relative pt-8 pb-16 container mx-auto px-4 z-10">
        <div className="hero-container-compact">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center flex flex-col items-center justify-center"
          >
            {/* Transform Label */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.8 }}
              className="inline-block -mb-8"
            >
              <span className="px-4 py-2 rounded-xl flex flex-row gap-3 items-center bg-white/10 text-xs text-white/90 backdrop-blur-sm border border-white/20 shadow-lg">
                <WandSparkles className="w-5 h-5 text-cyan-300" />
                <p className="font-medium">
                  TRANSFORM YOUR COMPLIANCE WITH AI AUTOMATION
                </p>
              </span>
            </motion.div>

            {/* Main Logo */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4, duration: 1, ease: "easeOut" }}
              className="flex justify-center items-center -mb-12"
            >
              <RuleIQLogo
                variant="hero"
                size="2xl"
                className="w-full max-w-4xl hero-logo"
              />
            </motion.div>

            {/* Tagline */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="text-center mb-32"
            >
              <h2 className="text-4xl hero-tagline uppercase tracking-wider">
                A.I. COMPLIANCE AUTOMATED
              </h2>
            </motion.div>

            {/* Description - Moved below the fold */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.8 }}
              className="max-w-3xl mx-auto text-lg text-white/80 text-center leading-relaxed mb-12 mt-40"
            >
              Stop struggling with compliance management. Our AI-powered platform analyzes
              your business, creates personalized compliance strategies, and helps you
              execute them - all in real-time.
            </motion.p>
          </motion.div>
        </div>

        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="space-y-4 flex flex-col items-center justify-center"
          >
            <HoverBorderGradient
              className="bg-gradient-to-b from-[rgb(91,105,139)] to-[#828282] px-6 font-extralight py-3 text-[16]"
              onClick={() => router.push("/checkout?plan=professional")}
            >
              Start Free Trial
            </HoverBorderGradient>
            <p className="text-sm text-white/50">
              Try ruleIQ free for 30 days
            </p>
          </motion.div>
      </main>
      </AuroraBackground>

      {/* Product Benefits Section */}
      <div className="min-h-screen mt-32 w-full h-full flex flex-col items-center overflow-hidden relative bg-gradient-to-b from-[#040508] to-[#0C0F15]">
        <div className="flex flex-col bg-transparent justify-center items-center w-full relative">
          {/* Gradient Circle Background */}
          <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-gradient-radial from-[#293249] to-transparent opacity-40 blur-3xl"></div>

          {/* Section Header */}
          <div className="flex justify-center text-center mt-16 z-10">
            <HoverBorderGradient
              containerClassName="rounded-full"
              as="button"
              className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2"
            >
              <span>Benefits</span>
            </HoverBorderGradient>
          </div>

          <div className="w-[70%] flex flex-col mt-8 items-center justify-center relative z-10">
            <div className="absolute inset-x-0 top-[-50px] z-0 flex justify-center">
              <div
                className="absolute w-[400px] h-[200px] bg-[#5B698B]/40 opacity-80 blur-[80px]"
                style={{ borderRadius: "50%" }}
              />
              <div
                className="absolute w-[300px] h-[150px] bg-[#5B698B]/50 opacity-80 blur-[100px]"
                style={{ borderRadius: "50%" }}
              />
            </div>

            <p className="text-5xl bp3:text-xl bp4:text-3xl text-center font-light">
              Why Choose
            </p>
            <div className="relative flex items-center w-full justify-center mt-1">
              <div className="absolute -left-40 h-[1px] w-[30%] bg-gradient-to-l to-black from-[#8096D2]"></div>
              <div className="absolute -right-40 h-[1px] w-[30%] bg-gradient-to-r to-black from-[#8096D2]"></div>
            </div>
            <p className="text-5xl bp4:text-3xl bp3:text-xl text-center mt-2 bg-gradient-to-b from-[#8096D2] to-[#b7b9be] bg-clip-text text-transparent font-light leading-tight">
              ruleIQ for your business
            </p>
          </div>

          {/* Benefits Cards Grid */}
          <div className="grid grid-cols-2 bp1:grid-cols-1 mt-14 gap-8 mb-10 w-[80%] max-w-6xl">
            <BenefitCard
              title="Reduce Compliance Costs by 60%"
              description="Automate manual compliance tasks and reduce the need for external consultants with our AI-powered platform."
              stats="Average 60% cost reduction"
            />
            <BenefitCard
              title="Cut Audit Preparation Time by 75%"
              description="Maintain audit-ready documentation automatically with real-time evidence collection and gap analysis."
              stats="From weeks to days"
            />
            <BenefitCard
              title="Achieve 99.9% Compliance Accuracy"
              description="AI-driven monitoring ensures you never miss regulatory changes or compliance requirements."
              stats="99.9% accuracy rate"
            />
            <BenefitCard
              title="Scale Across Multiple Frameworks"
              description="Support for SOC 2, ISO 27001, HIPAA, GDPR, and 50+ other compliance frameworks in one platform."
              stats="50+ frameworks supported"
            />
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
      <div className="min-h-screen w-full h-full flex flex-col items-center relative bg-gradient-to-b from-[#0C0F15] to-[#0C0F16]">
        <div className="flex flex-col bg-transparent justify-center items-center w-full relative">
          {/* Gradient Circle Background */}
          <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-gradient-radial from-[#293249] to-transparent opacity-40 blur-3xl"></div>

          {/* Section Header */}
          <div className="flex justify-center text-center mt-32 z-10">
            <HoverBorderGradient
              containerClassName="rounded-full"
              as="button"
              className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2"
            >
              <span>Testimonials</span>
            </HoverBorderGradient>
          </div>

          <div className="w-[70%] flex flex-col mt-8 items-center justify-center relative z-10">
            <div className="absolute inset-x-0 top-[-50px] z-0 flex justify-center">
              <div
                className="absolute w-[400px] h-[200px] bg-[#5B698B]/40 opacity-80 blur-[80px]"
                style={{ borderRadius: "50%" }}
              />
              <div
                className="absolute w-[300px] h-[150px] bg-[#5B698B]/50 opacity-80 blur-[100px]"
                style={{ borderRadius: "50%" }}
              />
            </div>

            <p className="text-5xl bp3:text-xl bp4:text-3xl text-center font-light">
              Trusted by
            </p>
            <div className="relative flex items-center w-full justify-center mt-1">
              <div className="absolute -left-40 h-[1px] w-[30%] bg-gradient-to-l to-black from-[#8096D2]"></div>
              <div className="absolute -right-40 h-[1px] w-[30%] bg-gradient-to-r to-black from-[#8096D2]"></div>
            </div>
            <p className="text-5xl bp4:text-3xl bp3:text-xl text-center mt-2 bg-gradient-to-b from-[#8096D2] to-[#b7b9be] bg-clip-text text-transparent font-light leading-tight">
              Industry leaders worldwide
            </p>
          </div>

          {/* Testimonials Grid */}
          <div className="grid grid-cols-3 bp1:grid-cols-2 bp6:grid-cols-1 mt-14 gap-8 mb-10 w-[90%] max-w-7xl">
            <TestimonialCard
              quote="ruleIQ reduced our SOC 2 audit preparation time from 6 weeks to just 3 days. The automated evidence collection is a game-changer."
              author="Sarah Chen"
              title="CISO, TechFlow Solutions"
              company="Fortune 500 Technology Company"
              rating={5}
            />
            <TestimonialCard
              quote="We achieved HIPAA compliance 75% faster with ruleIQ. The AI-powered gap analysis identified issues we didn't even know existed."
              author="Dr. Michael Rodriguez"
              title="Chief Compliance Officer"
              company="HealthCare Innovations"
              rating={5}
            />
            <TestimonialCard
              quote="The real-time monitoring and automated reporting saved us over $200K in compliance costs last year. ROI was immediate."
              author="Jennifer Walsh"
              title="VP of Risk Management"
              company="Global Financial Services"
              rating={5}
            />
            <TestimonialCard
              quote="Managing multiple compliance frameworks used to be a nightmare. NexCompli made it seamless across all our international operations."
              author="David Kim"
              title="Head of Compliance"
              company="International Manufacturing Corp"
              rating={5}
            />
            <TestimonialCard
              quote="The platform's intuitive interface and comprehensive documentation made our ISO 27001 certification process incredibly smooth."
              author="Lisa Thompson"
              title="Information Security Manager"
              company="CloudTech Enterprises"
              rating={5}
            />
            <TestimonialCard
              quote="ruleIQ's AI insights helped us proactively address compliance gaps before they became issues. Outstanding platform."
              author="Robert Martinez"
              title="Chief Risk Officer"
              company="RegionalBank Holdings"
              rating={5}
            />
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="min-h-screen w-full h-full flex flex-col z-0 items-center relative bg-gradient-to-b from-[#0C0F15] to-[#0C0F16]">
        <div className="flex mt-96 flex-col bg-transparent justify-center items-center w-full relative">
          {/* Gradient Circle Background */}
          <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-gradient-radial from-[#293249] to-transparent opacity-40 blur-3xl"></div>

          {/* Button */}
          <div className="flex justify-center text-center bp1:mt-32 bp4:mt-44 mt-0 z-10">
            <HoverBorderGradient
              containerClassName="rounded-full"
              as="button"
              className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2"
            >
              <span>Features</span>
            </HoverBorderGradient>
          </div>

          {/* Text & Gradient Borders */}
          <div className="w-[70%] flex flex-col mt-8 items-center justify-center relative z-10">
            <div className="absolute inset-x-0 top-[-50px] z-0 flex justify-center">
              {/* Outer Soft Glow - Larger Ellipse */}
              <div
                className="absolute w-[400px] h-[200px] bg-[#5B698B]/40 opacity-80 blur-[80px]"
                style={{ borderRadius: "50%" }}
              />

              {/* Inner Glow - Smaller & Brighter Ellipse */}
              <div
                className="absolute w-[300px] h-[150px] bg-[#5B698B]/50 opacity-80 blur-[100px]"
                style={{ borderRadius: "50%" }}
              />
            </div>
            {/* First Line */}
            <p className="text-5xl bp3:text-xl bp4:text-3xl text-center font-light">
              Feature packed to Make
            </p>

            {/* Borders (Shifted Further Left & Right) */}
            <div className="relative flex items-center w-full justify-center mt-1">
              <div className="absolute -left-40 h-[1px] w-[30%] bg-gradient-to-l to-black from-[#8096D2]"></div>
              <div className="absolute -right-40 h-[1px] w-[30%] bg-gradient-to-r to-black from-[#8096D2]"></div>
            </div>

            {/* Second Line */}
            <p className="text-5xl bp4:text-3xl bp3:text-xl text-center mt-2 bg-gradient-to-b from-[#8096D2] to-[#b7b9be] bg-clip-text text-transparent font-light leading-tight">
              Compliance management easier and automated
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-3 bp1:grid-cols-2 bp6:grid-cols-1 mt-14 gap-0 mb-10">
            <FeatureCard
              title="Smart Gap Analysis"
              text="AI-powered compliance gap identification ensures your organization meets all regulatory requirements with automated evidence collection."
              icon={<MousePointerClick className="w-20 h-20" />}
            />
            <FeatureCard
              title="Real-time Monitoring"
              text="Access real-time insights and track compliance metrics across all frameworks in one unified dashboard to quickly address issues."
              icon={<Gauge className="w-20 h-20" />}
            />
            <FeatureCard
              title="Policy Automation"
              text="Automate policy creation and maintenance with AI-driven suggestions to improve your compliance posture with less effort."
              icon={<TrendingUpIcon className="w-20 h-20" />}
            />
            <FeatureCard
              title="Risk Assessment"
              text="AI agents continuously assess compliance risks, monitor regulatory changes, and provide actionable insights in real time."
              icon={<Shield className="w-20 h-20" />}
            />
            <FeatureCard
              title="Evidence Collection"
              text="Automated evidence gathering and documentation management help you maintain comprehensive audit trails effortlessly."
              icon={<FileCheck className="w-20 h-20" />}
            />
            <FeatureCard
              title="Team Collaboration"
              text="Centralize and streamline your compliance workflows. Enable seamless collaboration across teams with role-based access controls."
              icon={<Users className="w-20 h-20" />}
            />
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div className="min-h-screen w-full h-full flex flex-col items-center relative bg-gradient-to-b from-[#0C0F16] to-[#040508]">
        <div className="flex flex-col bg-transparent justify-center items-center w-full relative">
          {/* Gradient Circle Background */}
          <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-gradient-radial from-[#293249] to-transparent opacity-40 blur-3xl"></div>

          {/* Section Header */}
          <div className="flex justify-center text-center mt-32 z-10">
            <HoverBorderGradient
              containerClassName="rounded-full"
              as="button"
              className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2"
            >
              <span>Pricing</span>
            </HoverBorderGradient>
          </div>

          <div className="w-[70%] flex flex-col mt-8 items-center justify-center relative z-10">
            <div className="absolute inset-x-0 top-[-50px] z-0 flex justify-center">
              <div
                className="absolute w-[400px] h-[200px] bg-[#5B698B]/40 opacity-80 blur-[80px]"
                style={{ borderRadius: "50%" }}
              />
              <div
                className="absolute w-[300px] h-[150px] bg-[#5B698B]/50 opacity-80 blur-[100px]"
                style={{ borderRadius: "50%" }}
              />
            </div>

            <p className="text-5xl bp3:text-xl bp4:text-3xl text-center font-light">
              Simple, transparent
            </p>
            <div className="relative flex items-center w-full justify-center mt-1">
              <div className="absolute -left-40 h-[1px] w-[30%] bg-gradient-to-l to-black from-[#8096D2]"></div>
              <div className="absolute -right-40 h-[1px] w-[30%] bg-gradient-to-r to-black from-[#8096D2]"></div>
            </div>
            <p className="text-5xl bp4:text-3xl bp3:text-xl text-center mt-2 bg-gradient-to-b from-[#8096D2] to-[#b7b9be] bg-clip-text text-transparent font-light leading-tight">
              pricing for every business
            </p>
          </div>

          {/* Pricing Cards Grid - New Payment-Enabled */}
          <div className="mt-14 mb-10 w-[90%] max-w-6xl">
            <PricingSection 
              showHeader={false}
              onSelectPlan={(planId) => router.push(`/checkout?plan=${planId}`)}
            />
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="flex w-full mt-32 flex-col bg-gradient-to-b to-[#040508] from-[#0C0F15] bg-transparent justify-center items-center relative">
        {/* Gradient Circle Background */}
        <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-gradient-radial from-[#293249] to-transparent opacity-40 blur-3xl"></div>

        <div className="w-[70%] flex flex-col mt-16 items-center justify-center relative z-10">
          {/* First Line */}
          <p className="text-5xl text-center bp6:text-3xl">
            Are you ready to transform
          </p>

          {/* Second Line */}
          <p className="text-5xl text-center bp6:text-3xl mt-2 bg-gradient-to-b from-[#8096D2] to-[#b7b9be] bg-clip-text text-transparent leading-tight">
            your Compliance Management?
          </p>
        </div>

        <div className="flex mt-14 flex-col gap-8 items-center w-full justify-center">
          <motion.button
            className="group relative font-light overflow-hidden border-[2px] border-[#5B698B] rounded-full bg-gradient-to-b from-black to-[rgb(65,64,64)] h-[43px] w-[191px] text-white backdrop-blur-sm transition-colors hover:bg-[rgba(0,0,0,0.30)]"
            onMouseMove={handleMouseMove}
            onHoverStart={() => setIsHovered1(true)}
            onHoverEnd={() => setIsHovered1(false)}
            onClick={() => router.push("/checkout?plan=professional")}
          >
            <span className="relative z-10">Start Free Trial</span>
            {isHovered1 && (
              <motion.div
                className="absolute inset-0 z-0"
                animate={{
                  background: [
                    `radial-gradient(40px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(255,255,255,0.15), transparent 50%)`,
                  ],
                }}
                transition={{ duration: 0.15 }}
              />
            )}
          </motion.button>

          <motion.button
            className="group relative border-[2px] font-light border-[#5B698B] overflow-hidden rounded-full bg-gradient-to-b from-[rgb(91,105,139)] to-[#414040] h-[43px] w-[191px] text-white backdrop-blur-sm transition-colors hover:bg-[rgba(255,255,255,0.2)]"
            onMouseMove={handleMouseMove}
            onHoverStart={() => setIsHovered2(true)}
            onHoverEnd={() => setIsHovered2(false)}
            onClick={() => router.push("/login")}
          >
            <span className="relative z-10">Get Started</span>
            {isHovered2 && (
              <motion.div
                className="absolute inset-0 z-0"
                animate={{
                  background: [
                    `radial-gradient(40px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(255,255,255,0.2), transparent 50%)`,
                  ],
                }}
                transition={{ duration: 0.15 }}
              />
            )}
          </motion.button>
        </div>

        {/* Footer */}
        <div className="border-t-[#333B4F] w-[90%] border-[1px] mt-10"></div>
        <footer className="w-full flex flex-row justify-center items-center py-10">
          <div className="flex flex-row w-[90%] justify-evenly bp2:flex-col-reverse bp2:items-center bp2:gap-8">
            {/* Brand and Contact Info */}
            <div className="flex flex-col items-center gap-4">
              <h2 className="text-[#C5CDE3] bp3:text-5xl text-7xl font-light">
                <span className="font-light">rule</span><span className="font-bold">IQ</span><span className="font-light">.io</span>
              </h2>
              <div className="flex flex-row gap-3 items-end">
                <Mail className="w-4 h-4 text-[#8096D2]" />
                <a
                  href="mailto:contact@ruleiq.io"
                  className="font-light text-[#C5CDE3] hover:text-[#8096D2] transition-colors underline text-sm"
                >
                  contact@ruleiq.io
                </a>
              </div>
              <div className="flex flex-row gap-3 items-end">
                <MapPin className="w-4 h-4 text-[#8096D2]" />
                <p className="font-light text-[#C5CDE3] text-sm">
                  Global Compliance Solutions
                </p>
              </div>
            </div>

            {/* Quick Links */}
            <div className="flex flex-row gap-16 bp3:flex-col bp3:gap-8">
              {/* Company Section */}
              <div>
                <h3 className="text-[#C5CDE3] text-2xl font-bold mb-4">
                  Company
                </h3>
                <nav className="flex flex-col text-gray-400 gap-1 items-center">
                  <a
                    href="/about"
                    className="hover:text-[#8096D2] transition-colors"
                  >
                    About Us
                  </a>
                  <a
                    href="/privacy"
                    className="hover:text-[#8096D2] transition-colors"
                  >
                    Privacy Policy
                  </a>
                  <a
                    href="/terms"
                    className="hover:text-[#8096D2] transition-colors"
                  >
                    Terms of Service
                  </a>
                  <a
                    href="/support"
                    className="hover:text-[#8096D2] transition-colors"
                  >
                    Support
                  </a>
                </nav>
              </div>

              {/* Resources Section */}
              <div>
                <h3 className="text-[#C5CDE3] text-2xl font-bold mb-4">
                  Resources
                </h3>
                <nav className="flex flex-col text-gray-400 gap-1 items-center">
                  <a
                    href="/documentation"
                    className="hover:text-[#8096D2] transition-colors"
                  >
                    Documentation
                  </a>
                  <a
                    href="/blog"
                    className="hover:text-[#8096D2] transition-colors"
                  >
                    Blog
                  </a>
                  <a
                    href="/help"
                    className="hover:text-[#8096D2] transition-colors"
                  >
                    Help Center
                  </a>
                  <a
                    href="/api"
                    className="hover:text-[#8096D2] transition-colors"
                  >
                    API Reference
                  </a>
                </nav>
              </div>
            </div>
          </div>
        </footer>

        <div className="w-full flex justify-center text-gray-400 text-sm font-light mb-3 items-center">
          <p>All rights reserved &copy; 2025 ruleIQ.io</p>
        </div>
      </div>
    </div>
  );
}