import React from "react";
import { motion } from "framer-motion";
import { logos } from "@/data/logo";

const SVGRenderer = ({ svgString }: { svgString: string }) => {
  const cleanedSvg = svgString.replace(
    '<path fill="#ffffff" d="M0 0h192.744v192.744H0V0z"></path>',
    ""
  );
  return <div dangerouslySetInnerHTML={{ __html: cleanedSvg }} />;
};

const LogoMarquee = () => {
  return (
    <div className="relative w-full overflow-hidden py-8">
      <motion.div
        className="flex w-max items-center gap-16"
        animate={{
          x: ["0%", "-50%"], // Moves half of the duplicated list
        }}
        transition={{
          ease: "linear",
          duration: 10, // Adjust speed for smooth scrolling
          repeat: Infinity,
        }}
      >
        {/* Duplicate logos twice to create seamless scrolling */}
        {[...logos, ...logos].map((logo, index) => (
          <div
            key={index}
            className="flex-shrink-0 w-32 h-full flex items-center justify-center"
          >
            <div className="w-24 h-full opacity-50">
              <SVGRenderer svgString={logo.logo} />
            </div>
          </div>
        ))}
      </motion.div>
    </div>
  );
};

export default LogoMarquee;
