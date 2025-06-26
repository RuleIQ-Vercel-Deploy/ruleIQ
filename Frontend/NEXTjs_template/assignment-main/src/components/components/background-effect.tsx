import React from "react";

const BackgroundEffects = () => {
  return (
    <div className="fixed inset-0 w-full overflow-hidden pointer-events-none">
      {/* Permanent Grid Background */}
      <div className="fixed inset-0 bg-grid-black/[0.04] dark:bg-grid-white/[0.06] bg-[length:50px_50px]">
        {/* Gradient Overlay for Grid Fade-out */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/30 to-white dark:via-black/30 dark:to-black" />
      </div>

      {/* Scrollable Effects Container */}
      <div className="sticky top-0 h-screen w-full">
        {/* Triangle Gradient */}
        <div className="absolute z-10">
          <div
            className="absolute w-[500px] h-[500px] opacity-80"
            style={{
              background:
                "radial-gradient(circle, rgba(255,255,255,0.35) 40%, transparent 90%)",
              clipPath: "polygon(50% 0%, 100% 100%, 0% 100%)",
              filter: "blur(180px)",
              top: "-250px",
              left: "50%",
              transform: "translateX(-50%)",
            }}
          />
        </div>

        {/* Ambient Glow */}
        <div
          className="absolute 
            w-[800px] h-[600px]
            bg-gradient-to-b from-white/15 to-transparent
            blur-[150px]
            opacity-70"
        />

        {/* Central Soft Glow */}
        <div
          className="absolute
            w-[450px] h-[450px]
            bg-white/35
            blur-[150px]
            opacity-75"
        />

        {/* Radial Mask */}
        <div className="absolute inset-0 dark:bg-black bg-white [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]" />
      </div>
    </div>
  );
};

export default BackgroundEffects;
