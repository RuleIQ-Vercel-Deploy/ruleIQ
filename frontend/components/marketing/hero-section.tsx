'use client';

import { Button } from '@/components/ui/button';

export function HeroSection() {
  return (
    <section className="py-20 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-6">
          Streamline Your Compliance Journey
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-powered compliance automation for UK SMBs
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg">Get Started</Button>
          <Button variant="outline" size="lg">Learn More</Button>
        </div>
      </div>
    </section>
  );
}
