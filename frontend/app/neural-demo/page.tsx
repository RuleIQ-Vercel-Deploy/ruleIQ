'use client';

import Hero from '@/components/ui/neural-network-hero';

export default function NeuralDemoPage() {
  return (
    <div className="relative min-h-screen bg-black">
      {/* Neural Network Hero Demo */}
      <Hero 
        title="Neural Network Background Demo"
        description="Experience the sophisticated CPPN shader background with purple and silver accents. This cutting-edge visual effect creates a dynamic, AI-inspired atmosphere perfect for RuleIQ."
        badgeText="WebGL Powered"
        badgeLabel="DEMO"
        ctaButtons={[
          { text: "Back to Home", href: "/", primary: true },
          { text: "View Dashboard", href: "/dashboard" }
        ]}
        microDetails={[
          "CPPN Shader Technology",
          "60 FPS Performance",
          "Purple & Silver Theme"
        ]}
      />
    </div>
  );
}