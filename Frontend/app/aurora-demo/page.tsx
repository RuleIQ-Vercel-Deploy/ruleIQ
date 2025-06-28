"use client";

import { AuroraBackground } from "@/components/ui/aurora-background";

export default function AuroraDemo() {
  return (
    <AuroraBackground>
      <div className="relative flex flex-col gap-4 items-center justify-center px-4">
        <div className="text-3xl md:text-7xl font-bold dark:text-white text-center">
          Background lights are cool you know.
        </div>
        <div className="font-extralight text-base md:text-4xl dark:text-neutral-200 py-4 text-center">
          And this, is a chemical burn.
        </div>
        <button className="bg-black dark:bg-white rounded-full w-fit text-white dark:text-black px-4 py-2">
          Debug now
        </button>
      </div>
    </AuroraBackground>
  );
}