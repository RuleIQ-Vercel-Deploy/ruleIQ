'use client';

import { Button } from '@/components/ui/button';

export function HeroSection() {
  return (
    <section className="px-4 py-20">
      <div className="mx-auto max-w-4xl text-center">
        <h1 className="mb-6 text-4xl font-bold">Streamline Your Compliance Journey</h1>
        <p className="mb-8 text-xl text-gray-600">AI-powered compliance automation for UK SMBs</p>
        <div className="flex justify-center gap-4">
          <Button size="lg">Get Started</Button>
          <Button variant="outline" size="lg">
            Learn More
          </Button>
        </div>
      </div>
    </section>
  );
}
