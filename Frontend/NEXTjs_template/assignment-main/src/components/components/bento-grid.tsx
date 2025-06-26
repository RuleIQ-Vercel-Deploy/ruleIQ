"use client";

import type React from "react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Cog, UserCircle } from "lucide-react";
import { BorderBeam } from "../magicui/border-beam";
import RadarTargetingCard from "./radar-tragetting-card";
import BarGraph3D from "./bar-graph";
import PieChart3D from "./pie-charts";

export default function BentoGrid() {
  return (
    <div className="min-h-screen w-full flex justify-center items-center bg-transparent p-6">
      <div className=" max-w-7xl">
        <div className="bp1:grid hidden grid-rows-2 gap-6 mt-28 bp6:h-[2000px] h-[1200px] bp6:mt-[280px]  place-items-center">
          <div className="grid bp6:grid-cols-1  grid-cols-2 gap-6 bp6:h-[1600px]  h-[800px]  place-items-center">
            <Card className="h-[70%]  w-[350px] bg-gradient-to-br from-[#2E3139] to-[#1E2536] overflow-hidden relative group">
              <div className="relative h-full bg-gradient-to-br from-[#2E3139] to-[#1E2536] rounded-xl overflow-hidden border-0">
                <BorderBeam
                  duration={6}
                  delay={3}
                  size={700}
                  className="from-transparent via-blue-500 to-transparent"
                />
                {/* Radar Effect */}
                <div className="absolute inset-0 mb-24 flex items-center justify-center">
                  {/* Outer Radar Circle */}
                  <div className="relative w-[300px] h-[300px] rounded-full border border-blue-300/30 flex items-center justify-center">
                    {/* Rotating Scan Line */}
                    <motion.div
                      className="absolute w-[300px] h-[300px] rounded-full bg-gradient-to-r from-blue-300/40 to-transparent opacity-30"
                      animate={{ rotate: 360 }}
                      transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: "linear",
                      }}
                    />

                    {/* Expanding Waves */}
                    <motion.div
                      className="absolute w-[200px] h-[200px] rounded-full border border-blue-300/20"
                      initial={{ scale: 0.5, opacity: 0 }}
                      animate={{ scale: 1.5, opacity: 1 }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                    />
                    <motion.div
                      className="absolute w-[250px] h-[250px] rounded-full border border-blue-300/10"
                      initial={{ scale: 0.7, opacity: 0 }}
                      animate={{ scale: 2, opacity: 1 }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                    />

                    {/* Pulsating Center Signal */}
                    <motion.div
                      className="absolute w-[20px] h-[20px] bg-blue-400 rounded-full"
                      animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                    />

                    {/* User Icons */}
                    {[
                      { className: "top-4 left-8", delay: 0 },
                      { className: "bottom-10 right-10", delay: 0.5 },
                      { className: "top-10 right-16", delay: 1 },
                      { className: "bottom-16 left-12", delay: 1.5 },
                    ].map((item, index) => (
                      <motion.div
                        key={index}
                        className={`absolute ${item.className}`}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        transition={{
                          duration: 1.5,
                          repeat: Infinity,
                          repeatType: "mirror",
                          delay: item.delay,
                        }}
                      >
                        <UserCircle size={28} className="text-blue-300/90" />
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Card Content */}
                <div className="absolute bottom-0 w-full p-6 bg-gradient-to-t from-black/60 to-transparent">
                  <h3 className="text-[16px] text-white">
                    Reach Target Audience2
                  </h3>
                  <p className="text-gray-400 text-sm">
                    Pinpoint the perfect audience with precision. Our AI-driven
                    targeting ensures every message resonates where it matters
                    most.
                  </p>
                </div>
              </div>
            </Card>
            {/* Right side card */}
            <RadarTargetingCard />
          </div>
          <div className="flex-row bp6:flex-col flex bp6:-mt-[350px] -mt-44 gap-6 h-[70%]">
            {/* Top center card */}
            <Card className="flex-1 w-[350px] h-[350px] bg-gradient-to-br from-[#2E3139] to-[#1E2536] border-0 overflow-hidden relative group">
              <CardContent className="h-full  p-6 flex relative flex-col gap-4 items-center justify-center">
                <BorderBeam
                  duration={6}
                  delay={3}
                  size={300}
                  className="from-transparent via-blue-500 to-transparent"
                />
                <div className="flex gap-4">
                  <div className="p-1 relative rounded-xl">
                    <BorderBeam
                      duration={6}
                      delay={3}
                      size={100}
                      className="from-transparent via-blue-500 to-transparent"
                    />
                    <div className="p-3 relative rounded-xl bg-[rgba(59,67,88)]">
                      <BorderBeam
                        duration={6}
                        delay={3}
                        size={100}
                        className="from-transparent via-blue-500 to-transparent"
                      />
                      {/* Rotating and Glowing Cog Icon */}
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{
                          repeat: Infinity,
                          duration: 5,
                          ease: "linear",
                        }}
                        className="drop-shadow-[0_0_10px_#7586B4] filter"
                      >
                        <Cog className="w-24 h-24 text-[#7586B4]" />
                      </motion.div>
                    </div>

                    {/* Glowing Line Positioned at Right Center */}
                    <div className="w-28 h-[1px] absolute -right-[107px] top-1/2 -translate-y-1/2 bg-[#7586B4]  shadow-[0_0_10px_#7586B4]"></div>

                    {/* "Gen AI Powered" Text Positioned Above the Line */}
                    <div className="absolute -right-[95px] top-[calc(50%-14px)] -translate-y-1/2 text-[#7586B4] text-[10px] font-light">
                      Gen AI Powered
                    </div>
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  <h3 className="text-[16px] text-white">
                    Marketing made Easier
                  </h3>
                  <p className="text-sm text-gray-400">
                    Save time and simplify campaign management. Let automated
                    workflows handle the heavy lifting, so you can focus on
                    creativity.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Bottom center card */}
            <Card className="flex-1 h-[350px] bg-gradient-to-br from-[#2E3139] to-[#1E2536] border-0 overflow-hidden relative group">
              <CardContent className="h-full w-[350px]  relative p-6 flex flex-col gap-4 items-center justify-center">
                <BorderBeam
                  duration={6}
                  delay={3}
                  size={300}
                  className="from-transparent via-blue-500 to-transparent"
                />
                <div className="flex gap-4">
                  <div className="p-1 relative rounded-xl">
                    <div className="p-3 relative rounded-xl bg-[rgba(59,67,88)]">
                      {/* Animated Bar Graph */}
                      <motion.div
                        animate={{ y: [0, -10, 0] }}
                        transition={{
                          repeat: Infinity,
                          duration: 1.5,
                          ease: "easeInOut",
                        }}
                        className="drop-shadow-[0_0_10px_#7586B4] filter"
                      >
                        <BarGraph3D />
                      </motion.div>
                    </div>
                  </div>

                  {/* Static Pie Chart */}
                  <div className="w-[124px] h-[124px] flex items-center justify-center relative rounded-xl bg-[rgba(59,67,88)]">
                    {/* Animated Bar Graph */}
                    <motion.div
                      animate={{ y: [0, -10, 0] }}
                      transition={{
                        repeat: Infinity,
                        duration: 1.5,
                        ease: "easeInOut",
                      }}
                      className="drop-shadow-[0_0_10px_#7586B4] filter"
                    >
                      <PieChart3D />
                    </motion.div>
                  </div>
                </div>

                <div className="mt-4 space-y-2">
                  <h3 className="text-[16px] text-white">
                    Smart Marketing Insights
                  </h3>
                  <p className="text-sm text-gray-400">
                    Unlock actionable data to guide every decision. Stay ahead
                    of trends, refine your strategies, and make confident moves
                    with powerful analytics.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
        <div className="bp1:hidden grid grid-cols-3 gap-6 h-[800px] place-items-center">
          {/* Left side card */}
          <Card className="h-[70%]  w-[350px] bg-gradient-to-br from-[#2E3139] to-[#1E2536] overflow-hidden relative group">
            <div className="relative h-full bg-gradient-to-br from-[#2E3139] to-[#1E2536] rounded-xl overflow-hidden border-0">
              <BorderBeam
                duration={6}
                delay={3}
                size={700}
                className="from-transparent via-blue-500 to-transparent"
              />
              {/* Radar Effect */}
              <div className="absolute inset-0 mb-24 flex items-center justify-center">
                {/* Outer Radar Circle */}
                <div className="relative w-[300px] h-[300px] rounded-full border border-blue-300/30 flex items-center justify-center">
                  {/* Rotating Scan Line */}
                  <motion.div
                    className="absolute w-[300px] h-[300px] rounded-full bg-gradient-to-r from-blue-300/40 to-transparent opacity-30"
                    animate={{ rotate: 360 }}
                    transition={{
                      duration: 4,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                  />

                  {/* Expanding Waves */}
                  <motion.div
                    className="absolute w-[200px] h-[200px] rounded-full border border-blue-300/20"
                    initial={{ scale: 0.5, opacity: 0 }}
                    animate={{ scale: 1.5, opacity: 1 }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  />
                  <motion.div
                    className="absolute w-[250px] h-[250px] rounded-full border border-blue-300/10"
                    initial={{ scale: 0.7, opacity: 0 }}
                    animate={{ scale: 2, opacity: 1 }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  />

                  {/* Pulsating Center Signal */}
                  <motion.div
                    className="absolute w-[20px] h-[20px] bg-blue-400 rounded-full"
                    animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  />

                  {/* User Icons */}
                  {[
                    { className: "top-4 left-8", delay: 0 },
                    { className: "bottom-10 right-10", delay: 0.5 },
                    { className: "top-10 right-16", delay: 1 },
                    { className: "bottom-16 left-12", delay: 1.5 },
                  ].map((item, index) => (
                    <motion.div
                      key={index}
                      className={`absolute ${item.className}`}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        repeatType: "mirror",
                        delay: item.delay,
                      }}
                    >
                      <UserCircle size={28} className="text-blue-300/90" />
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Card Content */}
              <div className="absolute bottom-0 w-full p-6 bg-gradient-to-t from-black/60 to-transparent">
                <h3 className="text-[16px] text-white">
                  Reach Target Audience
                </h3>
                <p className="text-gray-400 text-sm">
                  Pinpoint the perfect audience with precision. Our AI-driven
                  targeting ensures every message resonates where it matters
                  most.
                </p>
              </div>
            </div>
          </Card>

          {/* Center column with two cards */}
          <div className="flex flex-col  gap-6 h-[70%]">
            {/* Top center card */}
            <Card className="flex-1 bg-gradient-to-br from-[#2E3139] to-[#1E2536] border-0 overflow-hidden relative group">
              <CardContent className="h-full p-6 flex relative flex-col gap-4 items-center justify-center">
                <BorderBeam
                  duration={6}
                  delay={3}
                  size={300}
                  className="from-transparent via-blue-500 to-transparent"
                />
                <div className="flex gap-4">
                  <div className="p-1 relative rounded-xl">
                    <BorderBeam
                      duration={6}
                      delay={3}
                      size={100}
                      className="from-transparent via-blue-500 to-transparent"
                    />
                    <div className="p-3 relative rounded-xl bg-[rgba(59,67,88)]">
                      <BorderBeam
                        duration={6}
                        delay={3}
                        size={100}
                        className="from-transparent via-blue-500 to-transparent"
                      />
                      {/* Rotating and Glowing Cog Icon */}
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{
                          repeat: Infinity,
                          duration: 5,
                          ease: "linear",
                        }}
                        className="drop-shadow-[0_0_10px_#7586B4] filter"
                      >
                        <Cog className="w-24 h-24 text-[#7586B4]" />
                      </motion.div>
                    </div>

                    {/* Glowing Line Positioned at Right Center */}
                    <div className="w-28 h-[1px] absolute -right-[107px] top-1/2 -translate-y-1/2 bg-[#7586B4]  shadow-[0_0_10px_#7586B4]"></div>

                    {/* "Gen AI Powered" Text Positioned Above the Line */}
                    <div className="absolute -right-[95px] top-[calc(50%-14px)] -translate-y-1/2 text-[#7586B4] text-[10px] font-light">
                      Gen AI Powered
                    </div>
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  <h3 className="text-[16px] text-white">
                    Marketing made Easier
                  </h3>
                  <p className="text-sm text-gray-400">
                    Save time and simplify campaign management. Let automated
                    workflows handle the heavy lifting, so you can focus on
                    creativity.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Bottom center card */}
            <Card className="flex-1 bg-gradient-to-br from-[#2E3139] to-[#1E2536] border-0 overflow-hidden relative group">
              <CardContent className="h-full relative p-6 flex flex-col gap-4 items-center justify-center">
                <BorderBeam
                  duration={6}
                  delay={3}
                  size={300}
                  className="from-transparent via-blue-500 to-transparent"
                />
                <div className="flex gap-4">
                  <div className="p-1 relative rounded-xl">
                    <div className="p-3 relative rounded-xl bg-[rgba(59,67,88)]">
                      {/* Animated Bar Graph */}
                      <motion.div
                        animate={{ y: [0, -10, 0] }}
                        transition={{
                          repeat: Infinity,
                          duration: 1.5,
                          ease: "easeInOut",
                        }}
                        className="drop-shadow-[0_0_10px_#7586B4] filter"
                      >
                        <BarGraph3D />
                      </motion.div>
                    </div>
                  </div>

                  {/* Static Pie Chart */}
                  <div className="w-[124px] h-[124px] flex items-center justify-center relative rounded-xl bg-[rgba(59,67,88)]">
                    {/* Animated Bar Graph */}
                    <motion.div
                      animate={{ y: [0, -10, 0] }}
                      transition={{
                        repeat: Infinity,
                        duration: 1.5,
                        ease: "easeInOut",
                      }}
                      className="drop-shadow-[0_0_10px_#7586B4] filter"
                    >
                      <PieChart3D />
                    </motion.div>
                  </div>
                </div>

                <div className="mt-4 space-y-2">
                  <h3 className="text-[16px] text-white">
                    Smart Marketing Insights
                  </h3>
                  <p className="text-sm text-gray-400">
                    Unlock actionable data to guide every decision. Stay ahead
                    of trends, refine your strategies, and make confident moves
                    with powerful analytics.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right side card */}
          <RadarTargetingCard />
        </div>
      </div>
    </div>
  );
}
