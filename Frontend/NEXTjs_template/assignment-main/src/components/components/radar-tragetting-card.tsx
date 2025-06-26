import React from "react";
import { UserCircle } from "lucide-react";
import { Lightning } from "@phosphor-icons/react";
import { motion } from "framer-motion";
import { Card } from "../ui/card";
import { BorderBeam } from "../magicui/border-beam";

const RadarTargetingCard = () => {
  // Starting positions on the outer circle (radius = 140px)
  const startPositions = [
    { x: 140 * Math.cos(Math.PI / 4), y: 140 * Math.sin(Math.PI / 4) }, // Top Right
    {
      x: 140 * Math.cos((3 * Math.PI) / 4),
      y: 140 * Math.sin((3 * Math.PI) / 4),
    }, // Top Left
    {
      x: 140 * Math.cos((5 * Math.PI) / 4),
      y: 140 * Math.sin((5 * Math.PI) / 4),
    }, // Bottom Left
    {
      x: 140 * Math.cos((7 * Math.PI) / 4),
      y: 140 * Math.sin((7 * Math.PI) / 4),
    }, // Bottom Right
  ];

  return (
    <Card className="h-[70%] w-[350px] bp6:-mt-[450px] bg-gradient-to-br from-[#2E3139] to-[#1E2536] overflow-hidden relative group">
      <div className="relative h-full bg-gradient-to-br from-[#2E3139] to-[#1E2536] rounded-xl overflow-hidden border-0">
        <BorderBeam
          duration={6}
          delay={3}
          size={700}
          className="from-transparent via-blue-500 to-transparent"
        />
        <div className="absolute inset-0 flex items-center justify-center -translate-y-12">
          {/* Outer Circle */}
          <div className="relative w-[280px] h-[280px] rounded-full border border-blue-300/30 flex items-center justify-center">
            {/* Middle Circle */}
            <div className="absolute w-[180px] h-[180px] rounded-full border border-blue-300/40" />
            {/* Inner Circle */}
            <div className="absolute w-[80px] h-[80px] rounded-full border border-blue-300/50" />

            {/* Animated User Icons */}
            {startPositions.map((pos, index) => (
              <motion.div
                key={index}
                className="absolute"
                animate={{
                  x: [pos.x, 0, pos.x],
                  y: [pos.y, 0, pos.y],
                  opacity: [1, 0.5, 1],
                  scale: [1, 0.6, 1],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  repeatType: "loop",
                  ease: "easeInOut",
                  times: [0, 0.5, 1],
                  delay: index * 0.75,
                }}
              >
                <UserCircle size={28} className="text-blue-300/90" />
              </motion.div>
            ))}

            {/* Central Lightning Icon */}
            <motion.div
              className="absolute text-[#7586B4]"
              initial={{
                scale: 0.8,
                opacity: 0.8,
                filter: "drop-shadow(0px 0px 10px #7586B4)",
              }}
              animate={{
                scale: 1,
                opacity: 1,
                filter: "drop-shadow(0px 0px 20px #7586B4)",
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                repeatType: "mirror",
                ease: "easeInOut",
              }}
            >
              <Lightning size={100} className="fill-[#7586B4]" />
            </motion.div>
          </div>
        </div>

        {/* Card Content */}
        <div className="absolute bottom-0 w-full p-6 bg-gradient-to-t from-black/60 to-transparent">
          <h3 className="text-[16px] text-white">
            Intelligent Agents to Optimize your Reach
          </h3>
          <p className="text-gray-400 text-sm">
            Scale and refine your marketing with AI-powered agents. They track
            performance in real-time to help you reach more customers
            efficiently.
          </p>
        </div>
      </div>
    </Card>
  );
};

export default RadarTargetingCard;
